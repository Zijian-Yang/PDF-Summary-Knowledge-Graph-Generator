import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
import aiofiles
import aiohttp

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Slack应用
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# 用于跟踪正在处理的PDF文件
processing_pdfs = set()

# 异步函数：下载文件
async def download_file(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, mode='wb') as f:
                    await f.write(await response.read())
                logger.info(f"文件已下载: {file_path}")
                return True
            else:
                logger.error(f"文件下载失败: {response.status}")
                return False

# 异步函数：运行run.py
async def run_script():
    process = await asyncio.create_subprocess_exec(
        'python3', '../run.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        if "GraphMaker2_png.py 运行成功" in line.decode():
            return True
    return False

# 处理所有消息事件
@app.event("message")
async def handle_message(event, say):
    if "files" in event:
        await handle_file_shared(event, say)
    else:
        await say("请直接发送PDF文件。")

# 处理文件共享事件
async def handle_file_shared(event, say):
    try:
        file_info = app.client.files_info(file=event["files"][0]["id"])
        file_url = file_info["file"]["url_private_download"]
        file_name = file_info["file"]["name"]

        if not file_name.lower().endswith('.pdf'):
            await say("请上传PDF文件。")
            return

        if file_name in processing_pdfs:
            await say(f"文件 {file_name} 正在处理中，请稍后。")
            return

        processing_pdfs.add(file_name)

        input_pdf_path = os.path.join('..', 'input.pdf')

        download_success = await download_file(file_url, input_pdf_path)
        if not download_success:
            await say("文件下载失败，请重试。")
            processing_pdfs.remove(file_name)
            return

        await say(f"已接收文件 {file_name}，开始处理...")

        run_success = await run_script()
        if not run_success:
            await say("处理过程中出现错误，请重试。")
            processing_pdfs.remove(file_name)
            return

        try:
            async with aiofiles.open(os.path.join('..', 'output.txt'), mode='r') as f:
                output_text = await f.read()
            await say(output_text)

            await app.client.files_upload(
                channels=event["channel"],
                file=os.path.join('..', "knowledge_graph.png"),
                title="知识图谱"
            )
        except Exception as e:
            logger.error(f"发送结果失败: {str(e)}")
            await say("处理完成，但发送结果时出错。")
            return

        await say("处理完成！")

    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}")
        await say("处理文件时出现错误，请重试。")
    finally:
        if 'file_name' in locals():
            processing_pdfs.remove(file_name)

# 错误处理
@app.error
async def error_handler(error, body, logger):
    logger.error(f"错误: {error}")
    logger.error(f"请求体: {body}")

# 主函数
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

