"""
E2E测试 - Simulation/Report/Graph API集成测试

测试核心API端点:
1. Report API: list, get
2. Simulation API: list, create, get
3. Graph API: build, get

运行方式:
    pytest tests/e2e/test_integration_flows.py -v
"""

import pytest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)


# ============ 测试夹具 ============

@pytest.fixture(autouse=True)
def setup_env():
    """设置测试环境变量"""
    os.environ.setdefault('FLASK_ENV', 'test')
    os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-for-integration')
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


# ============ Report API 测试 ============

class TestReportAPI:
    """Report API端点测试"""

    def test_list_reports_empty(self, client):
        """空报告列表"""
        response = client.get('/api/report/list')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_list_reports_with_limit(self, client):
        """带limit参数的报告列表"""
        response = client.get('/api/report/list?limit=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) <= 5

    def test_list_reports_with_simulation_filter(self, client):
        """按simulation_id过滤"""
        response = client.get('/api/report/list?simulation_id=nonexistent')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_get_nonexistent_report(self, client):
        """获取不存在的报告 - 返回空数据或404"""
        response = client.get('/api/report/nonexistent-id-123')
        # 报告不存在时返回404或空数据200
        assert response.status_code in (200, 404)
        data = response.get_json()
        if response.status_code == 404:
            assert data['success'] is False

    def test_get_report_sections_nonexistent(self, client):
        """获取不存在报告的章节 - 返回空数据"""
        response = client.get('/api/report/nonexistent-id-123/sections')
        # 报告不存在时返回空sections或404
        assert response.status_code in (200, 404)

    def test_get_report_metrics_nonexistent(self, client):
        """获取不存在报告的指标"""
        response = client.get('/api/report/nonexistent-id-123/metrics')
        # 报告不存在时返回404或空数据
        assert response.status_code in (200, 404)

    def test_generate_report_missing_fields(self, client):
        """生成报告缺少必需字段"""
        response = client.post('/api/report/generate', json={})
        assert response.status_code == 400

    def test_divination_report_missing_chart(self, client):
        """生成命理报告缺少chart字段"""
        response = client.post('/api/divination/report/generate', json={
            "analysis_result": {}
        })
        # 缺少chart时返回400或500（取决于验证时机）
        assert response.status_code in (400, 500)

    def test_divination_report_invalid_chart(self, client):
        """命理报告无效chart数据"""
        response = client.post('/api/divination/report/generate', json={
            "chart": {"invalid": "data"},
            "analysis_result": {}
        })
        # 可能是200（LLM处理）或500（LLM API错误）或400（验证失败）
        assert response.status_code in (200, 400, 500)


# ============ Simulation API 测试 ============

class TestSimulationAPI:
    """Simulation API端点测试

    注意: Simulation需要先有project才能创建。
    这里测试不需要project的端点（list, get）和参数验证。
    """

    def test_list_simulations_empty(self, client):
        """空模拟列表"""
        response = client.get('/api/simulation/list')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_create_simulation_missing_project_id(self, client):
        """创建模拟缺少project_id - 参数验证"""
        response = client.post('/api/simulation/create', json={
            "name": "Test Simulation",
            "description": "Missing project_id"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'project_id' in data.get('error', '').lower() or 'project' in data.get('error', '').lower()

    def test_create_simulation_nonexistent_project(self, client):
        """创建模拟使用不存在的project_id"""
        response = client.post('/api/simulation/create', json={
            "project_id": "nonexistent-project-123"
        })
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False

    def test_get_nonexistent_simulation(self, client):
        """获取不存在的模拟"""
        response = client.get('/api/simulation/nonexistent-id-456')
        # 返回404或空数据200
        assert response.status_code in (200, 404)

    def test_get_simulation_profiles_nonexistent(self, client):
        """获取不存在模拟的智能体"""
        response = client.get('/api/simulation/nonexistent-id-456/profiles')
        assert response.status_code in (200, 404)

    def test_start_simulation_missing_id(self, client):
        """启动模拟缺少ID"""
        response = client.post('/api/simulation/start', json={})
        assert response.status_code == 400

    def test_stop_simulation_missing_id(self, client):
        """停止模拟缺少ID"""
        response = client.post('/api/simulation/stop', json={})
        assert response.status_code == 400

    def test_simulation_run_status_nonexistent(self, client):
        """获取不存在模拟的运行状态"""
        response = client.get('/api/simulation/nonexistent-id-456/run-status')
        assert response.status_code in (200, 404)

    def test_start_nonexistent_simulation(self, client):
        """启动不存在的模拟"""
        response = client.post('/api/simulation/start', json={
            "simulation_id": "nonexistent-sim-123"
        })
        # 返回404或400
        assert response.status_code in (400, 404)


# ============ Graph API 测试 ============

class TestGraphAPI:
    """Graph API端点测试

    注意: Graph build需要先创建project获取project_id。
    这里测试参数验证和无project的场景。
    """

    def test_build_graph_missing_project_id(self, client):
        """构建图谱缺少project_id"""
        response = client.post('/api/graph/build', json={
            "text": "Some text"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'project_id' in data.get('error', '').lower()

    def test_build_graph_nonexistent_project(self, client):
        """构建图谱使用不存在的project_id"""
        response = client.post('/api/graph/build', json={
            "project_id": "nonexistent-project-xyz"
        })
        # 返回404（项目不存在）或500（ZEP配置错误）
        assert response.status_code in (404, 500)

    def test_get_graph_nonexistent(self, client):
        """获取不存在的图谱"""
        response = client.get('/api/graph/data/nonexistent-graph-id')
        # 返回404或500
        assert response.status_code in (404, 500)

    def test_list_graphs(self, client):
        """列出图谱"""
        response = client.get('/api/graph/project/list')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_build_graph_empty_body(self, client):
        """构建图谱空请求体"""
        response = client.post('/api/graph/build', json={})
        assert response.status_code == 400


# ============ Health Check ============

class TestHealthCheck:
    """健康检查端点"""

    def test_health_endpoint(self, client):
        """后端健康检查"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('status') == 'ok'
