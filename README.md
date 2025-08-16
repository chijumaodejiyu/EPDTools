# EPD Tools - 电子纸显示图像处理工具

![EPD Tools Logo](img/bar_size.png)

EPD Tools是一个用于电子纸显示(EPD)的图像处理工具，支持多种抖动算法和串口数据传输。

## 主要功能

- 支持三种抖动算法：黑白、红白、红黑白
- 交互式命令行界面
- 中英双语支持
- 串口数据传输功能
- 自动创建输出目录

## 安装要求

- Python 3.6+
- OpenCV (`pip install opencv-python`)
- numpy (`pip install numpy`)
- pyserial (`pip install pyserial`)

## 使用说明

1. 运行程序：
   ```bash
   python main.py
   ```

2. 选择语言：
   ```
   Select language/选择语言: [1] English [2] 中文
   > 
   ```

3. 输入图片路径（默认：test/input.jpg）：
   ```
   Enter image path (default: test/input.jpg): 
   输入图片路径 (默认: test/input.jpg): 
   ```

4. 输入COM端口（默认：COM3）：
   ```
   Enter COM port (default: COM3): 
   输入COM端口 (默认: COM3): 
   ```

5. 选择抖动方式：
   ```
   Select dithering method [1] Black & White [2] Red & White [3] Red-Black-White (default: 1): 
   选择抖动方式 [1] 黑白 [2] 红白 [3] 红黑白 (默认: 1): 
   ```

6. 程序将自动处理图片并保存结果到output目录。

## 项目结构

```
EPDTools/
├── main.py                # 主程序
├── models/
│   ├── Dithering.py       # 抖动算法实现
│   ├── ImgProcesser.py    # 图像处理
│   └── serial.py         # 串口通信
├── img/                   # 图片资源
├── output/                # 输出目录
└── test/                  # 测试图片
```

## 示例

处理图片并发送到COM3端口：
```bash
python main.py
> 选择语言/Select language: [1] English [2] 中文
> 2
> 输入图片路径 (默认: test/input.jpg): test/sample.jpg
> 输入COM端口 (默认: COM3): COM3
> 选择抖动方式 [1] 黑白 [2] 红白 [3] 红黑白 (默认: 1): 3
```

## 许可证

本项目采用 [MIT License](LICENSE)
