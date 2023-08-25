def on_buttonConnect_clicked(self):
    # 打开或关闭串口按钮
    if self._serial.isOpen():
        # 如果串口是打开状态则关闭
        self._serial.close()
        self.textBrowser.append('串口已关闭')
        self.buttonConnect.setText('打开串口')
        self.labelStatus.setProperty('isOn', False)
        self.labelStatus.style().polish(self.labelStatus)  # 刷新样式
        return

    # 根据配置连接串口
    name = self.comboBoxPort.currentText()
    if not name:
        QMessageBox.critical(self, '错误', '没有选择串口')
        return
    port = self._ports[name]
    #         self._serial.setPort(port)
    # 根据名字设置串口（也可以用上面的函数）
    self._serial.setPortName(port.systemLocation())
    # 设置波特率
    self._serial.setBaudRate(  # 动态获取,类似QSerialPort::Baud9600这样的吧
        getattr(QSerialPort, 'Baud' + self.comboBoxBaud.currentText()))
    # 设置校验位
    self._serial.setParity(  # QSerialPort::NoParity
        getattr(QSerialPort, self.comboBoxParity.currentText() + 'Parity'))
    # 设置数据位
    self._serial.setDataBits(  # QSerialPort::Data8
        getattr(QSerialPort, 'Data' + self.comboBoxData.currentText()))
    # 设置停止位
    self._serial.setStopBits(  # QSerialPort::Data8
        getattr(QSerialPort, self.comboBoxStop.currentText()))

    # NoFlowControl          没有流程控制
    # HardwareControl        硬件流程控制(RTS/CTS)
    # SoftwareControl        软件流程控制(XON/XOFF)
    # UnknownFlowControl     未知控制
    self._serial.setFlowControl(QSerialPort.NoFlowControl)
    # 读写方式打开串口
    ok = self._serial.open(QIODevice.ReadWrite)
    if ok:
        self.textBrowser.append('打开串口成功')
        self.buttonConnect.setText('关闭串口')
        self.labelStatus.setProperty('isOn', True)
        self.labelStatus.style().polish(self.labelStatus)  # 刷新样式
    else:
        self.textBrowser.append('打开串口失败')
        self.buttonConnect.setText('打开串口')
        self.labelStatus.setProperty('isOn', False)
        self.labelStatus.style().polish(self.labelStatus)  # 刷新样式