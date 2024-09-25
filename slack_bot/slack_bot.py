import os
import time
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import subprocess
import asyncio
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Slack应用
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# 创建一个线程池
executor = ThreadPoolExecutor(max_workers=5)

# 用于跟踪正在处理的PDF文件
processing_pdfs = set()

# 异步函数：下载文件
async def download_file(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, mode='wb') as f:
                    await f.write(await response.read())
                logger.info(f"File downloaded: {file_path}")
                return True
            else:
                logger.error(f"Failed to download file: {response.status}")
                return False

# 异步函数：运行run.py
async def run_script():
    process = await asyncio.create_subprocess_exec(
        'python3', '../run.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        logger.info("run.py executed successfully")
        return True
    else:
        logger.error(f"run.py execution failed: {stderr.decode()}")
        return False

# 处理文件共享事件
@app.event("file_shared")
async def handle_file_shared(event, say):
    try:
        # 获取文件信息
        file_info = app.client.files_info(file=event["file_id"])
        file_url = file_info["file"]["url_private_download"]
        file_name = file_info["file"]["name"]

        # 检查文件类型
        if not file_name.lower().endswith('.pdf'):
            await say("请上传PDF文件。")
            return

        # 检查是否已经在处理该文件
        if file_name in processing_pdfs:
            await say(f"文件 {file_name} 正在处理中，请稍后。")
            return

        processing_pdfs.add(file_name)

        # 设置文件路径
        input_pdf_path = os.environ.get("INPUT_PDF_PATH", "input.pdf")
        file_path = os.path.join('..', input_pdf_path)

        # 下载文件
        download_success = await download_file(file_url, file_path)
        if not download_success:
            await say("文件下载失败，请重试。")
            processing_pdfs.remove(file_name)
            return

        await say(f"已接收文件 {file_name}，开始处理...")

        # 运行run.py
        run_success = await run_script()
        if not run_success:
            await say("处理过程中出现错误，请重试。")
            processing_pdfs.remove(file_name)
            return

        # 读取output.txt
        output_file = os.environ.get("OUTPUT_FILE", "output.txt")
        try:
            async with aiofiles.open(os.path.join('..', output_file), mode='r') as f:
                output_text = await f.read()
        except FileNotFoundError:
            await say("无法找到输出文件，请重试。")
            processing_pdfs.remove(file_name)
            return

        # 发送输出文本
        await say(output_text)

        # 发送知识图谱图片
        try:
            await app.client.files_upload(
                channels=event["channel_id"],
                file=os.path.join('..', "knowledge_graph.png"),
                title="Knowledge Graph"
            )
        except Exception as e:
            logger.error(f"Failed to upload knowledge graph: {str(e)}")
            await say("无法上传知识图谱，但文本摘要已发送。")

        await say("处理完成！")

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        await say("处理文件时出现错误，请重试。")
    finally:
        if 'file_name' in locals():
            processing_pdfs.remove(file_name)

# 错误处理
@app.error
async def error_handler(error, body, logger):
    logger.error(f"Error: {error}")
    logger.error(f"Request body: {body}")

# 处理消息事件
@app.event("message")
async def handle_message(event, say):
    # 检查消息是否来自用户(不是bot)
    if "user" in event:
        await say(f"收到你的消息: {event['text']}")

# 处理应用提及事件
@app.event("app_mention")
async def handle_mentions(event, say):
    await say(f"谢谢你提到我! 你说: {event['text']}")

# 主函数
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

# 检测run.py是否运行成功
