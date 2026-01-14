# cdutAsyncSpider
一个基于智强教务 的大学教务接口获取 和 教务系统课表采集工具


## 项目概述

这是一个基于Python的异步爬虫脚本，以CDUT🦕为例。
用于登录CDUT教务系统并批量获取指定教室的课表信息。脚本采用异步编程模式，提高了数据获取效率，适用于需要批量查询教室使用情况的场景。

## 功能特点

- ✅ **异步编程**：使用`asyncio`和`httpx`实现异步HTTP请求，提高爬取效率
- ✅ **RSA加密**：自动获取公钥并对密码进行RSA加密，确保登录安全
- ✅ **自动登录**：模拟CAS单点登录流程，自动处理重定向和表单提交
- ✅ **批量获取**：支持同时获取多个教室的课表信息
- ✅ **本地保存**：将每个教室的课表以HTML格式保存到本地

## 安装与使用

### 安装依赖

```bash
pip install httpx[http2] pycryptodome
```

### 配置与运行

1. **修改个人信息**：在`main()`函数中配置用户名和密码
   ```python
   username = "你的学号/电话"
   password = "你的密码"
   ```

2. **配置查询参数**：
   - `rooms`：需要查询的教室列表，每个教室包含`jsid`(教室ID)、`jsmc`(教室名称)、`jsh`(教室号)等信息
   - `xnxq01id`：学年学期ID，格式如"2025-2026-1"表示2025-2026学年第一学期

3. **运行脚本**：
   ```bash
   python jwSpider.py

   或者在IDE中直接运行
   ```


## 核心功能详解

### 1. RSA密码加密

```python
async def get_rsa_password(self):
    url = "https://cas.paas.cdut.edu.cn/cas/jwt/publicKey"
    response = await self.client.get(url)
    pub_pem = response.text
    rsakey = RSA.import_key(pub_pem)
    cipher = PKCS1_v1_5.new(rsakey)
    cipher_text = cipher.encrypt(self.password.encode())
    return "__RSA__" + base64.b64encode(cipher_text).decode()
```

- 从服务器获取RSA公钥
- 使用公钥对密码进行加密
- 返回加密后的密码字符串，格式为`__RSA__`+base64编码的密文

### 2. CAS单点登录

```python
async def login(self):
    # 1. 获取execution参数
    res01 = await self.client.get(login_url)
    execution = re.search(r'name="execution" value="(.*?)"', res01.text).group(1)
    
    # 2. 构造登录参数
    encrypted_pw = await self.get_rsa_password()
    login_data = {...}
    
    # 3. 提交登录请求
    await self.client.post(login_url, data=login_data)
```

- 获取登录页面的`execution`参数
- 构造包含加密密码的登录表单
- 提交登录请求，自动处理重定向

### 3. 批量获取课表

```python
tasks = [spider.save_room_schedule(room, kbjcmsid, xnxq01id) for room in rooms]
await asyncio.gather(*tasks)
```

- 使用列表推导式创建多个异步任务
- 使用`asyncio.gather()`并发执行所有任务
- 提高课表获取效率

## 注意事项‼️

1. **隐私安全**：请不要将包含个人账号密码的代码公开分享
2. **使用频率**：请勿高频次运行脚本，避免给教务系统服务器带来过大压力
3. **依赖安装**：确保正确安装所有依赖库，特别是`pycryptodome`而非`Crypto`
4. **版本兼容**：建议使用Python 3.7或更高版本

## License

📕本项目采用 CC NC-SA 4.0 许可证开源

## 贡献者

- Github @ mloong
- Github @ KawasakiKusako
