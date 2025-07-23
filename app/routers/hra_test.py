# #!/usr/bin/env python3
# """
# HRA接口测试脚本
# 用于测试HRA报告解析接口是否正常工作
# """

# import requests
# import json
# import time
# import traceback

# class HRAInterfaceTester:
#     def __init__(self, base_url="http://localhost:8000"):
#         self.base_url = base_url
#         self.test_results = []
    
#     def log_test(self, test_name, success, message, response=None):
#         """记录测试结果"""
#         result = {
#             "test": test_name,
#             "success": success,
#             "message": message,
#             "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#             "response": response
#         }
#         self.test_results.append(result)
        
#         status = "✅ PASS" if success else "❌ FAIL"
#         print(f"{status} {test_name}: {message}")
#         if response and not success:
#             print(f"    响应: {response}")
    
#     def test_health_endpoint(self):
#         """测试健康检查接口"""
#         try:
#             response = requests.get(f"{self.base_url}/health", timeout=10)
#             if response.status_code == 200:
#                 self.log_test("健康检查", True, "服务正常运行", response.json())
#             else:
#                 self.log_test("健康检查", False, f"状态码: {response.status_code}", response.text)
#         except requests.exceptions.ConnectionError:
#             self.log_test("健康检查", False, "无法连接到服务器，请检查服务是否启动")
#         except Exception as e:
#             self.log_test("健康检查", False, f"请求异常: {str(e)}")
    
#     def test_hra_endpoint_basic(self):
#         """测试HRA接口基础功能"""
#         test_payload = {
#             "user_id": 12345,
#             "kbId": "1",
#             "report_interpret": True
#         }
        
#         try:
#             response = requests.post(
#                 f"{self.base_url}/knowledge_base_chat_with_hra/",
#                 json=test_payload,
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 data = response.json()
#                 if "code" in data and data["code"] == 200:
#                     self.log_test("HRA接口基础测试", True, "接口正常响应", data)
#                 else:
#                     self.log_test("HRA接口基础测试", False, "响应格式异常", data)
#             elif response.status_code == 404:
#                 # 这是预期的，因为用户数据可能不存在
#                 self.log_test("HRA接口基础测试", True, "接口正常，用户数据不存在（预期行为）", response.json())
#             else:
#                 self.log_test("HRA接口基础测试", False, f"HTTP状态码: {response.status_code}", response.text)
                
#         except requests.exceptions.Timeout:
#             self.log_test("HRA接口基础测试", False, "请求超时，可能是处理时间过长")
#         except requests.exceptions.ConnectionError:
#             self.log_test("HRA接口基础测试", False, "连接错误，检查服务器状态")
#         except Exception as e:
#             self.log_test("HRA接口基础测试", False, f"请求异常: {str(e)}")
    
#     def test_hra_endpoint_validation(self):
#         """测试HRA接口参数验证"""
#         # 测试无效参数
#         invalid_payloads = [
#             {"user_id": "invalid", "report_interpret": True},  # 无效user_id
#             {"user_id": 12345},  # 缺少report_interpret
#             {"user_id": 12345, "report_interpret": False},  # report_interpret为False
#             {},  # 空请求体
#         ]
        
#         for i, payload in enumerate(invalid_payloads):
#             try:
#                 response = requests.post(
#                     f"{self.base_url}/knowledge_base_chat_with_hra/",
#                     json=payload,
#                     timeout=10
#                 )
                
#                 if response.status_code == 400:
#                     self.log_test(f"参数验证测试{i+1}", True, "正确拒绝无效参数")
#                 elif response.status_code == 422:
#                     self.log_test(f"参数验证测试{i+1}", True, "Pydantic验证正常工作")
#                 else:
#                     self.log_test(f"参数验证测试{i+1}", False, f"应该返回400或422，实际: {response.status_code}")
                    
#             except Exception as e:
#                 self.log_test(f"参数验证测试{i+1}", False, f"请求异常: {str(e)}")
    
#     def test_database_connectivity(self):
#         """间接测试数据库连接"""
#         # 通过接口调用间接测试数据库连接
#         test_payload = {
#             "user_id": 99999,  # 使用不存在的用户ID
#             "kbId": "1",
#             "report_interpret": True
#         }
        
#         try:
#             response = requests.post(
#                 f"{self.base_url}/knowledge_base_chat_with_hra/",
#                 json=test_payload,
#                 timeout=15
#             )
            
#             if response.status_code == 404:
#                 self.log_test("数据库连接测试", True, "数据库查询正常（返回404表示连接正常但数据不存在）")
#             elif response.status_code == 500:
#                 error_msg = response.json().get("detail", "服务器内部错误")
#                 if "database" in error_msg.lower() or "connection" in error_msg.lower():
#                     self.log_test("数据库连接测试", False, f"数据库连接问题: {error_msg}")
#                 else:
#                     self.log_test("数据库连接测试", False, f"服务器错误: {error_msg}")
#             else:
#                 self.log_test("数据库连接测试", True, f"接口响应正常，状态码: {response.status_code}")
                
#         except Exception as e:
#             self.log_test("数据库连接测试", False, f"请求异常: {str(e)}")
    
#     def generate_curl_commands(self):
#         """生成用于手动测试的curl命令"""
#         print("\n" + "="*60)
#         print("🔧 手动测试的curl命令:")
#         print("-"*60)
        
#         # 健康检查
#         print("1. 健康检查:")
#         print(f"curl -X GET {self.base_url}/health")
        
#         # 基础HRA测试
#         print("\n2. HRA接口基础测试:")
#         basic_payload = {
#             "user_id": 12345,
#             "kbId": "1", 
#             "report_interpret": True
#         }
#         print(f"curl -X POST {self.base_url}/knowledge_base_chat_with_hra/ \\")
#         print(f"  -H 'Content-Type: application/json' \\")
#         print(f"  -d '{json.dumps(basic_payload)}'")
        
#         # 参数验证测试
#         print("\n3. 参数验证测试（应该返回错误）:")
#         invalid_payload = {
#             "user_id": 12345,
#             "report_interpret": False
#         }
#         print(f"curl -X POST {self.base_url}/knowledge_base_chat_with_hra/ \\")
#         print(f"  -H 'Content-Type: application/json' \\")
#         print(f"  -d '{json.dumps(invalid_payload)}'")
    
#     def analyze_logs(self):
#         """分析测试结果并提供建议"""
#         print("\n" + "="*60)
#         print("📊 测试结果分析:")
#         print("-"*60)
        
#         total_tests = len(self.test_results)
#         passed_tests = sum(1 for r in self.test_results if r["success"])
#         failed_tests = total_tests - passed_tests
        
#         print(f"总测试数: {total_tests}")
#         print(f"通过: {passed_tests}")
#         print(f"失败: {failed_tests}")
#         print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
#         if failed_tests > 0:
#             print("\n❌ 失败的测试:")
#             for result in self.test_results:
#                 if not result["success"]:
#                     print(f"  - {result['test']}: {result['message']}")
        
#         print("\n🔧 建议的调试步骤:")
        
#         # 根据测试结果给出具体建议
#         health_test = next((r for r in self.test_results if "健康检查" in r["test"]), None)
#         if health_test and not health_test["success"]:
#             print("1. 服务器未启动或端口错误")
#             print("   - 检查FastAPI服务是否运行")
#             print("   - 确认端口号是否正确")
#             print("   - 检查防火墙设置")
        
#         hra_test = next((r for r in self.test_results if "HRA接口基础测试" in r["test"]), None)
#         if hra_test and not hra_test["success"]:
#             if "timeout" in hra_test["message"].lower():
#                 print("2. 接口超时问题")
#                 print("   - 检查数据库连接是否正常")
#                 print("   - 查看应用日志中的错误信息")
#                 print("   - 检查LLM API调用是否卡住")
#             elif "500" in hra_test["message"]:
#                 print("2. 服务器内部错误")
#                 print("   - 查看应用错误日志")
#                 print("   - 检查导入的模块是否存在")
#                 print("   - 验证数据库配置")
        
#         print("\n📋 检查清单:")
#         print("□ FastAPI服务是否正常启动")
#         print("□ 所有Python依赖包是否安装")
#         print("□ 数据库服务是否运行")
#         print("□ 自定义模块路径是否正确")
#         print("□ 环境变量是否设置")
#         print("□ LLM API密钥是否配置")
#         print("□ 知识库服务是否可用")
    
#     def run_all_tests(self):
#         """运行所有测试"""
#         print("🚀 开始HRA接口测试...")
#         print("="*60)
        
#         # 运行各项测试
#         self.test_health_endpoint()
#         print()
        
#         self.test_hra_endpoint_basic()
#         print()
        
#         self.test_hra_endpoint_validation()
#         print()
        
#         self.test_database_connectivity()
        
#         # 生成手动测试命令
#         self.generate_curl_commands()
        
#         # 分析结果
#         self.analyze_logs()

# def main():
#     """主函数"""
#     print("HRA接口测试工具")
#     print("="*60)
    
#     # 获取服务器地址
#     base_url = input("请输入服务器地址 (默认: http://localhost:8000): ").strip()
#     if not base_url:
#         base_url = "http://localhost:8000"
    
#     # 创建测试器并运行测试
#     tester = HRAInterfaceTester(base_url)
#     tester.run_all_tests()
    
#     print("\n测试完成！")
#     print("如果发现问题，请查看上面的建议进行排查。")

# if __name__ == "__main__":
#     main()
# 测试脚本
import asyncio
from your_module import call_llm_for_interpretation

async def test():
    indicators = [{"指标名称": "钾", "数值": "-10"}]
    result = await call_llm_for_interpretation(
        system_name="血液系统",
        abnormal_indicators=indicators,
        system_description="",
        knowledge_context=""
    )
    print(result)

asyncio.run(test())