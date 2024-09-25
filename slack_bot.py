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

# 同步函数：下载文件
def download_file(url, file_path):
    return asyncio.run(_download_file(url, file_path))

async def _download_file(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"}) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, mode='wb') as f:
                    await f.write(await response.read())
                logger.info(f"文件已下载: {file_path}")
                return True
            else:
                logger.error(f"文件下载失败: {response.status}")
                return False

# 同步函数：运行run.py
def run_script():
    logger.info("Starting to run script...")
    result = asyncio.run(_run_script())
    logger.info(f"Script run result: {result}")
    return result

async def _run_script():
    current_dir = os.getcwd()
    logger.info(f"Current working directory: {current_dir}")
    
    process = await asyncio.create_subprocess_exec(
        'python3', 'run.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if stdout:
        logger.info(f'[run.py] stdout:\n{stdout.decode()}')
    if stderr:
        logger.error(f'[run.py] stderr:\n{stderr.decode()}')
    
    if "GraphMaker2_png.py 运行成功" in stdout.decode() or "GraphMaker2_png.py 运行完成" in stdout.decode():
        return True
    return False

# 处理文件
def process_file(file_info, say):
    try:
        file_id = file_info["id"]
        file_name = file_info["name"]
        file_url = file_info["url_private_download"]
        
        # 更安全地获取 channel_id
        channel_id = None
        if "channels" in file_info and file_info["channels"]:
            channel_id = file_info["channels"][0]
        elif "ims" in file_info and file_info["ims"]:
            channel_id = file_info["ims"][0]
        
        if not channel_id:
            logger.error(f"无法确定 channel_id: {file_info}")
            return

        if not file_name.lower().endswith('.pdf'):
            say(channel=channel_id, text="请上传PDF文件。")
            return

        if file_name in processing_pdfs:
            say(channel=channel_id, text=f"文件 {file_name} 正在处理中，请稍后。")
            return

        processing_pdfs.add(file_name)

        input_pdf_path = 'input.pdf'

        download_success = download_file(file_url, input_pdf_path)
        if not download_success:
            say(channel=channel_id, text="文件下载失败，请重试。")
            processing_pdfs.remove(file_name)
            return

        say(channel=channel_id, text=f"已接收文件 {file_name}，开始处理...")

        try:
            run_success = run_script()
            if not run_success:
                say(channel=channel_id, text="处理过程中出现错误，请查看日志以获取更多信息。")
                processing_pdfs.remove(file_name)
                return
        except Exception as e:
            logger.error(f"运行脚本时出错: {str(e)}")
            say(channel=channel_id, text=f"运行脚本时出现错误: {str(e)}")
            processing_pdfs.remove(file_name)
            return

        try:
            with open('output.txt', mode='r') as f:
                output_text = f.read()
            say(channel=channel_id, text=output_text)

            app.client.files_upload(
                channels=channel_id,
                file="knowledge_graph.png",
                title="知识图谱"
            )
        except Exception as e:
            logger.error(f"发送结果失败: {str(e)}")
            say(channel=channel_id, text="处理完成，但发送结果时出错。")
            return

        say(channel=channel_id, text="处理完成！")

    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}")
        if channel_id:
            say(channel=channel_id, text=f"处理文件时出现错误: {str(e)}")
    finally:
        if 'file_name' in locals():
            processing_pdfs.remove(file_name)

@app.event("file_created")
def handle_file_created(body, logger):
    logger.info(f"Received file_created event: {body}")
    event = body["event"]
    file_id = event.get("file_id")
    if file_id:
        try:
            file_info = app.client.files_info(file=file_id)["file"]
            process_file(file_info, app.client.chat_postMessage)
        except Exception as e:
            logger.error(f"Error processing file_created event: {e}")
    else:
        logger.warning("Received file_created event without file_id")

@app.event("file_shared")
def handle_file_shared(body, logger):
    logger.info(f"Received file_shared event: {body}")
    event = body["event"]
    file_id = event.get("file_id")
    channel_id = event.get("channel_id")
    if file_id:
        try:
            file_info = app.client.files_info(file=file_id)["file"]
            # 确保 file_info 包含 channel_id
            if "channels" not in file_info or not file_info["channels"]:
                file_info["channels"] = [channel_id]
            process_file(file_info, app.client.chat_postMessage)
        except Exception as e:
            logger.error(f"Error processing file_shared event: {e}")
    else:
        logger.warning("Received file_shared event without file_id")

@app.event("message")
def handle_message(event, say):
    if "files" not in event:
        say("请直接发送PDF文件。")

# 错误处理
@app.error
def error_handler(error, body, logger):
    logger.error(f"错误: {error}")
    logger.error(f"请求体: {body}")

# 主函数
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

