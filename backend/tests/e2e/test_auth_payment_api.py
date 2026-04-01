"""
E2E测试 - Auth/Payment API测试

测试认证和支付接口:
1. 用户注册
2. 用户登录
3. 获取当前用户信息
4. checkout/stripe 接口参数验证
5. checkout/wechat 接口参数验证

运行方式:
    pytest tests/e2e/test_auth_payment_api.py -v
"""

import pytest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)


# ============ 测试夹具 ============

@pytest.fixture(autouse=True)
def setup_env():
    """Set test environment variables before any app imports."""
    import os
    os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-for-e2e')
    os.environ['FLASK_ENV'] = 'test'
    os.environ['TEST_DATA_DIR'] = f'/tmp/fengxian-test-{os.getpid()}'
    yield


@pytest.fixture
def app(setup_env):
    """创建测试应用"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def clean_user():
    """清理测试用户"""
    from app.models.user import UserManager
    test_email = f"test_auth_{os.getpid()}@example.com"
    yield test_email
    # 清理
    try:
        user = UserManager.get_user_by_email(test_email)
        if user:
            UserManager.delete_user(user.id)
    except Exception:
        pass


@pytest.fixture
def auth_headers(client, clean_user):
    """获取认证 token"""
    # 注册
    client.post('/api/v1/auth/register', json={
        "email": clean_user,
        "password": "test123456",
        "nickname": "Test User"
    })
    # 登录
    response = client.post('/api/v1/auth/login', json={
        "email": clean_user,
        "password": "test123456"
    })
    data = response.get_json()
    if data and data.get('success'):
        token = data['data']['access_token']
        return {"Authorization": f"Bearer {token}"}
    return {}


# ============ Auth API 测试 ============

class TestAuthRegister:

    def test_register_success(self, client, clean_user):
        """测试成功注册"""
        response = client.post('/api/v1/auth/register', json={
            "email": clean_user,
            "password": "test123456",
            "nickname": "Test User"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']

    def test_register_missing_email(self, client):
        """测试注册 - 缺少邮箱"""
        response = client.post('/api/v1/auth/register', json={
            "password": "test123456"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '邮箱' in data['error']

    def test_register_missing_password(self, client, clean_user):
        """测试注册 - 缺少密码"""
        response = client.post('/api/v1/auth/register', json={
            "email": clean_user
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '密码' in data['error']

    def test_register_short_password(self, client, clean_user):
        """测试注册 - 密码太短"""
        response = client.post('/api/v1/auth/register', json={
            "email": clean_user,
            "password": "12345"  # 少于6位
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '6位' in data['error']

    def test_register_invalid_email(self, client, clean_user):
        """测试注册 - 无效邮箱格式"""
        response = client.post('/api/v1/auth/register', json={
            "email": "notanemail",
            "password": "test123456"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '邮箱' in data['error']

    def test_register_duplicate_email(self, client, clean_user):
        """测试注册 - 重复邮箱"""
        client.post('/api/v1/auth/register', json={
            "email": clean_user,
            "password": "test123456"
        })
        response = client.post('/api/v1/auth/register', json={
            "email": clean_user,
            "password": "test123456"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestAuthLogin:

    def test_login_success(self, client, clean_user):
        """测试成功登录"""
        # 先注册
        client.post('/api/v1/auth/register', json={
            "email": clean_user,
            "password": "test123456"
        })
        # 再登录
        response = client.post('/api/v1/auth/login', json={
            "email": clean_user,
            "password": "test123456"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']

    def test_login_wrong_password(self, client, clean_user):
        """测试登录 - 错误密码"""
        client.post('/api/v1/auth/register', json={
            "email": clean_user,
            "password": "test123456"
        })
        response = client.post('/api/v1/auth/login', json={
            "email": clean_user,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert '错误' in data['error']

    def test_login_nonexistent_user(self, client):
        """测试登录 - 用户不存在"""
        response = client.post('/api/v1/auth/login', json={
            "email": "nonexistent@example.com",
            "password": "test123456"
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False


class TestAuthMe:

    def test_me_success(self, client, auth_headers):
        """测试获取当前用户信息"""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'user_id' in data['data']
        assert 'email' in data['data']

    def test_me_no_token(self, client):
        """测试获取用户信息 - 无token"""
        response = client.get('/api/v1/auth/me')
        assert response.status_code == 401

    def test_me_invalid_token(self, client):
        """测试获取用户信息 - 无效token"""
        response = client.get('/api/v1/auth/me', headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401


# ============ Payment API 测试 ============

class TestPaymentCheckout:

    def test_checkout_missing_price_key(self, client, auth_headers):
        """测试checkout - 缺少price_key"""
        response = client.post('/api/v1/payments/checkout', headers=auth_headers, json={
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_checkout_invalid_price_key(self, client, auth_headers):
        """测试checkout - 无效price_key"""
        response = client.post('/api/v1/payments/checkout', headers=auth_headers, json={
            "price_key": "invalid_price",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '未知的价格方案' in data['error']

    def test_checkout_no_auth(self, client):
        """测试checkout - 未认证"""
        response = client.post('/api/v1/payments/checkout', json={
            "price_key": "pro_monthly"
        })
        assert response.status_code == 401


class TestPaymentWechat:

    def test_wechat_qr_missing_price_key(self, client, auth_headers):
        """测试wechat - 缺少price_key"""
        response = client.post('/api/v1/payments/wechat/qr', headers=auth_headers, json={
            "description": "Test"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_wechat_qr_invalid_price_key(self, client, auth_headers):
        """测试wechat - 无效price_key"""
        response = client.post('/api/v1/payments/wechat/qr', headers=auth_headers, json={
            "price_key": "invalid_price",
            "description": "Test"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '未知的价格方案' in data['error']

    def test_wechat_qr_no_auth(self, client):
        """测试wechat - 未认证"""
        response = client.post('/api/v1/payments/wechat/qr', json={
            "price_key": "pro_monthly"
        })
        assert response.status_code == 401
