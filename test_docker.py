#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Docker 配置测试"""

import sys
import os

def test_docker_config():
    """测试 Docker 配置文件"""
    print("[TEST] 测试 Docker 配置...")
    
    # 测试1: 检查 Dockerfile 是否存在
    print("测试1: 检查 Dockerfile")
    dockerfile_path = "Dockerfile"
    if os.path.exists(dockerfile_path):
        print("[PASS] Dockerfile 存在")
    else:
        print("[FAIL] Dockerfile 不存在")
        return False
    
    # 测试2: 检查 docker-compose.yml 是否存在
    print("测试2: 检查 docker-compose.yml")
    compose_path = "docker-compose.yml"
    if os.path.exists(compose_path):
        print("[PASS] docker-compose.yml 存在")
    else:
        print("[FAIL] docker-compose.yml 不存在")
        return False
    
    # 测试3: 检查 .dockerignore 是否存在
    print("测试3: 检查 .dockerignore")
    ignore_path = ".dockerignore"
    if os.path.exists(ignore_path):
        print("[PASS] .dockerignore 存在")
    else:
        print("[FAIL] .dockerignore 不存在")
        return False
    
    # 测试4: 检查 Dockerfile 内容
    print("测试4: 检查 Dockerfile 内容")
    with open(dockerfile_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        assert "FROM python" in content, "缺少基础镜像"
        assert "WORKDIR" in content, "缺少工作目录设置"
        assert "requirements.txt" in content, "缺少依赖文件复制"
        assert "EXPOSE" in content, "缺少端口暴露"
        assert "streamlit" in content, "缺少启动命令"
    print("[PASS] Dockerfile 内容检查通过")
    
    # 测试5: 检查 docker-compose.yml 内容
    print("测试5: 检查 docker-compose.yml 内容")
    with open(compose_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "services:" in content, "缺少 services 定义"
        assert "agent:" in content, "缺少 agent 服务"
        assert "ports:" in content, "缺少端口映射"
        assert "environment:" in content, "缺少环境变量"
        assert "volumes:" in content, "缺少数据卷挂载"
    print("[PASS] docker-compose.yml 内容检查通过")
    
    # 测试6: 检查 requirements.txt 是否存在
    print("测试6: 检查 requirements.txt")
    req_path = "requirements.txt"
    if os.path.exists(req_path):
        print("[PASS] requirements.txt 存在")
    else:
        print("[FAIL] requirements.txt 不存在")
        return False
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("[INFO] Docker 配置测试")
    print("="*60)
    
    try:
        success = test_docker_config()
        
        print("\n" + "="*60)
        if success:
            print("[PASS] 所有测试通过！")
            print("\n部署说明:")
            print("1. 构建镜像: docker build -t ai-agent .")
            print("2. 运行容器: docker run -p 8501:8501 ai-agent")
            print("3. 或使用 compose: docker-compose up -d")
        else:
            print("[FAIL] 测试失败！")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
