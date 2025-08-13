import multiprocessing
import time


def run_mcp():
    from src_mcp.mcp_server.server.mcp_server import main as main_mcp

    main_mcp()


# def run_bilibili():
#     from service.media.bilibili import main as main_mcip_bilibili
#     main_mcip_bilibili()

if __name__ == "__main__":
    # 创建两个进程
    process_mcp = multiprocessing.Process(target=run_mcp)
    # process_bilibili = multiprocessing.Process(target=run_bilibili)

    # 启动进程
    process_mcp.start()
    # process_bilibili.start()

    # 可选：等待它们结束（如果是长期运行的服务，可能不需要 join）
    try:
        while True:
            time.sleep(1)  # 防止主进程退出
    except KeyboardInterrupt:
        print("\n终止服务...")
        process_mcp.terminate()
        # process_bilibili.terminate()
