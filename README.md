# 隐私计算平台互联互通协议

本仓库存放隐私计算平台互联互通协议（接口）文档。请注意当前的接口、协议文档还不是最终稳定版，不排除某些接口可能会做变更。

协议文档地址：[https://www.secretflow.org.cn/docs/interconnection/](https://www.secretflow.org.cn/docs/interconnection/)


当前已经定义的互联互通协议（接口）有:

- [ECDH-PSI 协议](./PPCA/open-protocols/ECDH-PSI.pdf)
- [SS-LR 协议](./PPCA/open-protocols/SS-LR.pdf)
- [SGB 协议](./PPCA/open-protocols/SGB.pdf)

## 目录结构

```
.
├── PPCA   # 存放隐私计算联盟归口的标准协议文件
├── docs   # 文档网站的网页源代码
└── interconnection    # 所有接口文件
    ├── common     # 通用的接口定义
    ├── handshake  # 所有握手协议相关接口
    │   ├── algos  # 算法层的握手协议接口
    │   ├── op     # 安全算子层的握手协议接口
    │   └── protocol_family    # 密码协议层的握手协议接口
    ├── legacy     # 目前已经废弃的接口文件
    ├── link       # 传输层接口
    ├── runtime    # 算法运行主体所用的接口
    └── service    # 访问第三方公共基础服务所用的接口

```

## 协议设计范式

目前所有的开放协议都分为握手协议和算法主体两部分，其中握手协议用于对齐算法版本、算法运行所需参数等，并遵循一些统一的范式：

1. 所有算法都复用同一套握手协议，即所有算法的握手请求都用的是 `interconnection/handshake/entry.proto` 中定义的 `HandshakeRequest`，所有算法的握手协商结果都使用 `HandshakeResponse` 格式。
2. 对于多个参与方的算法，我们为每个参与方赋予一个编号，称为 rank，rank 的数值从 0 开始依次递增。
3. 握手协议执行时，由非 0 参与方向 rank-0 发送 `HandshakeRequest`，rank-0 汇总所有参与方的请求后，得出一组公共参数，依次发送 `HandshakeResponse`，如果参数协商失败，则依次发送错误消息。
4. `HandshakeRequest` 中每一类具体的参数项，其命名风格一般为 XxxProposal，`HandshakeResponse` 中选定的参数项，其命名风格一般为 XxxResult。
5. 对于某些连续数值型参数，例如深度学习中的 learning_rate 等，我们假设无论参数选择几对功能无影响，对方都应该支持，这一类参数不需要协商，而是由 rank-0 选定一个数值，在 `HandshakeResponse` 中发给大家。
6. 对于一些可枚举的功能性参数，`HandshakeRequest` 用一个列表表示，表示发送者支持列表所列的功能；并且这个列表是有序的，表示发送者更加偏爱列表中靠前的参数。例如 ECDH-PSI 中的椭圆曲线(EC)类型，假如请求列表是 `[SM2, CURVE25519]`，则表示发送者同时支持 SM2 和 CURVE25519，如果其他参与方也同时支持这两种 EC，则协商者应当优先选择 SM2, 因为 SM2 排在前面。当然，如果多个参数方发送的列表顺序是矛盾的，协商者会优先满足大多数参与方的偏爱。

算法主体部分因算法而异，请以具体协议文档为准。


## 算法协议与传输层关系

算法协议中提到的 proto 一般并不直接用于 RPC 框架，而是用作跨语言、跨版本的序列化、反序列化工具使用。传输层只负责传输裸的二进制 buffer，不感知具体的 proto 格式，下图是一个示例：

```
 ┌─────────────┐                 ┌─────────────┐
 │  Algorithm  │                 │  Algorithm  │
 └──────┬──────┘                 └──────▲──────┘
        │Serialize                      │
        │proto                          │Deserialize
        │to buffer                      │buffer
 ┌──────▼──────┐                 ┌──────┴──────┐
 │  Transport  │     buffer      │  Transport  │
 │    layer    ├────────────────►│    layer    │
 └─────────────┘   http(s)/rpc   └─────────────┘
```

示例图：

1. 左侧的算法将 proto 序列化成 buffer，提交给传输层
2. 左侧传输层通过网络将数据发送到右侧传输层模块
3. 右侧算法获取传输层中的 buffer，反序列化成 proto
