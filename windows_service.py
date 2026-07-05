import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import sys
import asyncio
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('service.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SuperAgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SuperAgentService"
    _svc_display_name_ = "Super Agent AI量化投资智能体服务"
    _svc_description_ = "运行AI量化投资智能体，定时推送因子报告和市场分析到PushPlus"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self._running = True
        self._service_task = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self._running = False
        logger.info("Super Agent Service stopping...")

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logger.info("Super Agent Service started")
        self.main()

    def main(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from start_background_service import BackgroundService
        
        try:
            service = BackgroundService()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            task = loop.create_task(service.start())
            self._service_task = task
            
            loop.run_until_complete(task)
            
        except Exception as e:
            logger.error(f"Service error: {str(e)}", exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SuperAgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SuperAgentService)