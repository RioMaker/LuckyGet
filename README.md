# LuckyGetPlugin
好玩的插件，由良良子开发。

## 安装

配置完成 [LangBot](https://github.com/RockChinQ/LangBot) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/RioMaker/LuckyGet.git
```
或查看详细的[插件安装说明](https://docs.langbot.app/plugin/plugin-intro.html#%E6%8F%92%E4%BB%B6%E7%94%A8%E6%B3%95)

## 使用
```
/rp帮助：查看所有可用命令提示；

/rp：如果当日还没有记录，就随机生成并保存；有则直接取出来；
返回一个完整的当日“数值、吉凶签、幸运色、宜、忌”；

/rp记录：列出个人历史；

/rp删除 today|all：删除当日或全部运势；

/rp排行榜：显示今天所有用户的运势值按降序排名；默认只显示前 5 条，可自行调节；

/rp偷 @xxx：尝试从某人那偷运势。每天只能偷一次；
对方当日没有运势，或者运势为 0，就偷不到；
```