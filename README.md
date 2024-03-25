# 隐私计算平台开放算法协议

本仓库用于存放隐私计算平台开放算法协议接口，旨在将算法接口通过程序化设计语言 Protobuf 更加全面、精确地表述出来，帮助隐私计算平台开发者更好地实施互联互通改造，促进隐私计算算法的互联互通。

协议文档地址：[https://www.secretflow.org.cn/docs/interconnection/](https://www.secretflow.org.cn/docs/interconnection/)

## 协议组成

本仓库接口按照北京金融科技产业联盟（简称：金科联盟）隐私计算跨平台互联互通团体标准、信通院牵头隐私计算联盟互联互通团体标准要求设计，每一个算法协议均由“参数获取与校验”，“算法主体运行” 两部分组成，其中”参数获取“的方式两个标准略有差异：

- 金科联盟标准定义了完整的隐私计算平台框架，算法组件运行所需的配置全部由管理层的工作流配置模块（原名 DAG&CONF 模块）下发，算法协议直接从容器运行时获取参数
- 隐私计算联盟标准并未对算法组件之外的其它模块做过多假设，所有算法组件均通过自主握手协商的方式选定参数，从而使得开放算法协议可以独立部署、运行。

其余部分两个标准内容一致：

- 算法运行参数无论是管理层的工作流配置模块下发，还是自主握手协商选定，参数的数量、名称、作用在两个标准中是一样的
- 算法主体的运行流程、交互接口、以及每阶段的结束标记和判断逻辑在两标准中也是一样的

<table>
    <tr>
        <td></td>
        <td>金科联盟标准</td>
        <td>隐私计算联盟标准</td>
        <td>本仓库</td>
    <tr>
    <tr>
        <td>算法运行参数</td>
        <td>由管理层工作流配置模块下发</td>
        <td>参与方运行握手协商协议自行对齐参数</td>
        <td>基于握手协商的形式定义了完整的参数列表与接口，如对方采用金科联盟方式，可从容器运行时获取同名参数</td>
    <tr>
    <tr>
        <td>算法协议主体</td>
        <td colspan="2" style="text-align: center;">协议流程、接口一致</td>
        <td>定义了完整的协议主体运行所需接口</td>
    <tr>
</table>

### 相关仓库

| 仓库                                                                              | 说明                                 |
|---------------------------------------------------------------------------------|------------------------------------|
| [InterOp](https://github.com/secretflow/interop)                                | 金科联盟互联互通研究成果官方仓库                   |
| [caict-ppca/privacy-computing](https://github.com/caict-ppca/privacy-computing) | 隐私计算联盟互联互通研究成果官方仓库                 |
| [interconnection](https://github.com/secretflow/interconnection) (本仓库）          | 隐语收集、定义的互联互通开放算法协议接口、文档            |
| [interconnection-impl](https://github.com/secretflow/interconnection-impl)      | 互联互通开放算法协议的参考实现，支持 Python & C++ 语言 |

注: 仓库排名不分先后

## Interconnection 仓库结构

```
.
├── PPCA   # 存放隐私计算联盟归口的标准协议文件副本
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

当前已经定义的互联互通协议（接口）有:

- [ECDH-PSI 协议](./PPCA/open-protocols/ECDH-PSI.pdf)
- [SS-LR 协议](./PPCA/open-protocols/SS-LR.pdf)
- [SGB 协议](./PPCA/open-protocols/SGB.pdf)

注：本仓库收集、存放的互联互通接口仅为金科联盟、隐私计算联盟标准的子集，完整的接口、文档请参考各联盟的官方仓库。


## 握手协议设计原则

隐私计算联盟标准体系中所有算法协议都通过握手协商的方式对齐算法参数，整个过程较为复杂，此处做一些补充介绍。

握手协商协议的执行过程和接口设计遵循以下原则：

1. 所有算法都复用同一套握手协议，即所有算法的握手请求都用的是 `interconnection/handshake/entry.proto` 中定义的 `HandshakeRequest`，所有算法的握手协商结果都使用 `HandshakeResponse` 格式。
2. 对于多个参与方的算法，我们为每个参与方赋予一个编号，称为 rank，rank 的数值从 0 开始依次递增。
3. 握手协议执行时，由非 0 参与方向 rank-0 发送 `HandshakeRequest`，rank-0 汇总所有参与方的请求后，得出一组公共参数，依次发送 `HandshakeResponse`，如果参数协商失败，则依次发送错误消息。
4. `HandshakeRequest` 中每一类具体的参数项，其命名风格一般为 XxxProposal，`HandshakeResponse` 中选定的参数项，其命名风格一般为 XxxResult。
5. 对于某些连续数值型参数，例如深度学习中的 learning_rate 等，我们假设无论参数选择几对功能无影响，对方都应该支持，这一类参数不需要协商，而是由 rank-0 选定一个数值，在 `HandshakeResponse` 中发给大家。
6. 对于一些可枚举的功能性参数，`HandshakeRequest` 用一个列表表示，表示发送者支持列表所列的功能；并且这个列表是有序的，表示发送者更加偏爱列表中靠前的参数。例如 ECDH-PSI 中的椭圆曲线(EC)类型，假如请求列表是 `[SM2, CURVE25519]`，则表示发送者同时支持 SM2 和 CURVE25519，如果其他参与方也同时支持这两种 EC，则协商者应当优先选择 SM2, 因为 SM2 排在前面。当然，如果多个参数方发送的列表顺序是矛盾的，协商者会优先满足大多数参与方的偏爱。


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

