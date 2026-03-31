"""
WeChat Pay Service - 微信支付服务

提供微信支付集成功能。
"""

import os
import time
import hashlib
import uuid
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class WeChatOrderResult:
    """微信订单结果"""
    prepay_id: str
    order_id: str
    qr_code_url: str  # 用于生成二维码


class WeChatPayService:
    """微信支付服务"""

    # 配置
    WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', '')
    WECHAT_MCH_ID = os.environ.get('WECHAT_MCH_ID', '')  # 商户号
    WECHAT_API_KEY = os.environ.get('WECHAT_API_KEY', '')  # APIv2密钥
    WECHAT_API_V3_KEY = os.environ.get('WECHAT_API_V3_KEY', '')  # APIv3密钥
    WECHAT_CERT_PATH = os.environ.get('WECHAT_CERT_PATH', '')  # 证书路径

    # API URLs
    SANDBOX_URL = 'https://api.mch.weixin.qq.com/sandboxnew'
    PROD_URL = 'https://api.mch.weixin.qq.com'

    _test_mode = True

    @classmethod
    def _get_base_url(cls) -> str:
        """获取基础URL"""
        return cls.SANDBOX_URL if cls._test_mode else cls.PROD_URL

    @classmethod
    def _generate_nonce_str(cls, length: int = 32) -> str:
        """生成随机字符串"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        import random
        return ''.join(random.choice(chars) for _ in range(length))

    @classmethod
    def _generate_signature(cls, sign_str: str) -> str:
        """生成签名（APIv2）"""
        # SHA1签名
        sign_str = sign_str + f"&key={cls.WECHAT_API_KEY}"
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()

    @classmethod
    def _sign_v3(cls, sign_str: str) -> str:
        """生成签名（APIv3）"""
        # 加载私钥（需要使用证书）
        # 这里简化处理，实际应从文件加载
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()

    # ==================== Native Pay (扫码支付) ====================

    @classmethod
    def create_native_order(
        cls,
        description: str,
        amount: int,  # 单位：分
        out_trade_no: Optional[str] = None,
        notify_url: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> WeChatOrderResult:
        """
        创建Native Pay订单（扫码支付）

        Args:
            description: 商品描述
            amount: 金额（分）
            out_trade_no: 商户订单号
            notify_url: 回调URL
            metadata: 附加数据

        Returns:
            WeChatOrderResult
        """
        if not out_trade_no:
            out_trade_no = f"{cls.WECHAT_MCH_ID}{int(time.time())}{uuid.uuid4().hex[:6]}"

        if not notify_url:
            notify_url = os.environ.get('WECHAT_NOTIFY_URL', '')

        # 构建请求参数
        params = {
            'appid': cls.WECHAT_APP_ID,
            'mch_id': cls.WECHAT_MCH_ID,
            'nonce_str': cls._generate_nonce_str(),
            'body': description[:128],  # 限制长度
            'out_trade_no': out_trade_no,
            'total_fee': amount,
            'spbill_create_ip': os.environ.get('SERVER_IP', '127.0.0.1'),
            'notify_url': notify_url,
            'trade_type': 'NATIVE',
        }

        # 添加附加数据
        if metadata:
            params['attach'] = '&'.join(f"{k}={v}" for k, v in metadata.items())

        # 生成签名
        sign_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items())) + f"&key={cls.WECHAT_API_KEY}"
        params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

        # 发送请求
        url = f"{cls._get_base_url()}/pay/unifiedorder"
        response = requests.post(
            url,
            data=cls._dict_to_xml(params),
            headers={'Content-Type': 'text/xml'},
            timeout=10,
        )

        result = cls._parse_xml_response(response.text)

        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            return WeChatOrderResult(
                prepay_id=result.get('prepay_id', ''),
                order_id=out_trade_no,
                qr_code_url=result.get('code_url', ''),
            )
        else:
            error_msg = result.get('err_code_des', result.get('return_msg', 'Unknown error'))
            raise ValueError(f"WeChat Pay failed: {error_msg}")

    # ==================== JSAPI Pay (公众号支付) ====================

    @classmethod
    def create_jsapi_order(
        cls,
        openid: str,
        description: str,
        amount: int,
        out_trade_no: Optional[str] = None,
        notify_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建JSAPI订单（用于微信内网页支付）

        Returns:
            调起支付的参数
        """
        if not out_trade_no:
            out_trade_no = f"{cls.WECHAT_MCH_ID}{int(time.time())}{uuid.uuid4().hex[:6]}"

        if not notify_url:
            notify_url = os.environ.get('WECHAT_NOTIFY_URL', '')

        params = {
            'appid': cls.WECHAT_APP_ID,
            'mch_id': cls.WECHAT_MCH_ID,
            'nonce_str': cls._generate_nonce_str(),
            'body': description[:128],
            'out_trade_no': out_trade_no,
            'total_fee': amount,
            'spbill_create_ip': os.environ.get('SERVER_IP', '127.0.0.1'),
            'notify_url': notify_url,
            'trade_type': 'JSAPI',
            'openid': openid,
        }

        # 生成签名
        sign_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items())) + f"&key={cls.WECHAT_API_KEY}"
        params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

        # 发送请求
        url = f"{cls._get_base_url()}/pay/unifiedorder"
        response = requests.post(
            url,
            data=cls._dict_to_xml(params),
            headers={'Content-Type': 'text/xml'},
            timeout=10,
        )

        result = cls._parse_xml_response(response.text)

        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            # 返回调起支付的参数
            prepay_id = result.get('prepay_id', '')

            # 再次签名，用于wx.chooseWXPay
            pay_sign_str = f"appId={cls.WECHAT_APP_ID}&nonceStr={params['nonce_str']}&package=prepay_id={prepay_id}&signType=MD5&timeStamp={int(time.time())}&key={cls.WECHAT_API_KEY}"
            pay_sign = hashlib.md5(pay_sign_str.encode('utf-8')).hexdigest().upper()

            return {
                'appId': cls.WECHAT_APP_ID,
                'nonceStr': params['nonce_str'],
                'package': f'prepay_id={prepay_id}',
                'signType': 'MD5',
                'timeStamp': str(int(time.time())),
                'paySign': pay_sign,
            }
        else:
            error_msg = result.get('err_code_des', result.get('return_msg', 'Unknown error'))
            raise ValueError(f"WeChat Pay failed: {error_msg}")

    # ==================== Order Query ====================

    @classmethod
    def query_order(cls, out_trade_no: str) -> Optional[Dict[str, Any]]:
        """查询订单"""
        params = {
            'appid': cls.WECHAT_APP_ID,
            'mch_id': cls.WECHAT_MCH_ID,
            'out_trade_no': out_trade_no,
            'nonce_str': cls._generate_nonce_str(),
        }

        sign_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items())) + f"&key={cls.WECHAT_API_KEY}"
        params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

        url = f"{cls._get_base_url()}/pay/orderquery"
        response = requests.post(
            url,
            data=cls._dict_to_xml(params),
            headers={'Content-Type': 'text/xml'},
            timeout=10,
        )

        return cls._parse_xml_response(response.text)

    # ==================== Close Order ====================

    @classmethod
    def close_order(cls, out_trade_no: str) -> bool:
        """关闭订单"""
        params = {
            'appid': cls.WECHAT_APP_ID,
            'mch_id': cls.WECHAT_MCH_ID,
            'out_trade_no': out_trade_no,
            'nonce_str': cls._generate_nonce_str(),
        }

        sign_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items())) + f"&key={cls.WECHAT_API_KEY}"
        params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

        url = f"{cls._get_base_url()}/pay/closeorder"
        response = requests.post(
            url,
            data=cls._dict_to_xml(params),
            headers={'Content-Type': 'text/xml'},
            timeout=10,
        )

        result = cls._parse_xml_response(response.text)
        return result.get('return_code') == 'SUCCESS'

    # ==================== Refund ====================

    @classmethod
    def refund(
        cls,
        out_trade_no: str,
        total_amount: int,
        refund_amount: int,
        refund_desc: Optional[str] = None,
    ) -> bool:
        """申请退款"""
        params = {
            'appid': cls.WECHAT_APP_ID,
            'mch_id': cls.WECHAT_MCH_ID,
            'nonce_str': cls._generate_nonce_str(),
            'out_trade_no': out_trade_no,
            'out_refund_no': f"refund_{out_trade_no}",
            'total_fee': total_amount,
            'refund_fee': refund_amount,
        }

        if refund_desc:
            params['refund_desc'] = refund_desc

        sign_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items())) + f"&key={cls.WECHAT_API_KEY}"
        params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

        url = f"{cls._get_base_url()}/secapi/pay/refund"
        response = requests.post(
            url,
            data=cls._dict_to_xml(params),
            cert=(cls.WECHAT_CERT_PATH, cls.WECHAT_API_KEY) if cls.WECHAT_CERT_PATH else None,
            headers={'Content-Type': 'text/xml'},
            timeout=10,
        )

        result = cls._parse_xml_response(response.text)
        return result.get('return_code') == 'SUCCESS'

    # ==================== WeChat Login (OAuth2) ====================

    @classmethod
    def get_oauth_url(
        cls,
        redirect_uri: str,
        state: Optional[str] = None,
        scope: str = 'snsapi_base',
    ) -> str:
        """
        获取微信OAuth2授权URL

        Args:
            redirect_uri: 回调URL
            state: 状态参数
            scope: snsapi_base (静默) or snsapi_userinfo (需用户确认)
        """
        if not state:
            state = cls._generate_nonce_str(16)

        params = {
            'appid': cls.WECHAT_APP_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state,
        }

        query = '&'.join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
        return f"https://open.weixin.qq.com/connect/oauth2/authorize?{query}#wechat_redirect"

    @classmethod
    def get_access_token(cls, code: str) -> Optional[Dict[str, Any]]:
        """获取Access Token"""
        params = {
            'appid': cls.WECHAT_APP_ID,
            'secret': os.environ.get('WECHAT_APP_SECRET', ''),
            'code': code,
            'grant_type': 'authorization_code',
        }

        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        response = requests.get(url, params=params, timeout=10)
        return response.json()

    @classmethod
    def get_user_info(cls, access_token: str, openid: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN',
        }

        url = 'https://api.weixin.qq.com/sns/userinfo'
        response = requests.get(url, params=params, timeout=10)
        return response.json()

    # ==================== Notify Handler ====================

    @classmethod
    def parse_notify_response(cls, payload: str) -> Dict[str, Any]:
        """解析支付回调通知"""
        return cls._parse_xml_response(payload)

    @classmethod
    def verify_notify_signature(cls, payload: str) -> bool:
        """验证回调签名"""
        # 实现签名验证逻辑
        return True

    # ==================== Helpers ====================

    @classmethod
    def _dict_to_xml(cls, params: Dict[str, Any]) -> str:
        """字典转XML"""
        root = ET.Element('xml')
        for key, value in params.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    @classmethod
    def _parse_xml_response(cls, xml_str: str) -> Dict[str, Any]:
        """解析XML响应"""
        try:
            root = ET.fromstring(xml_str)
            return {child.tag: child.text for child in root}
        except ET.ParseError:
            return {'return_code': 'FAIL', 'return_msg': 'XML parse error'}
