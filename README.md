# region_checker

## 概要
region_checker は ROS (Robot Operating System) のパッケージで、事前に設定した地図上の領域に対して、位置情報がどの領域に属するかを識別できます。このパッケージは特に、ロボットの現在位置や目標位置が地図上のどの領域にあるかを確認するのに役立ちます。

たとえば、地図上に「A」と「B」という二つの領域を設定して、ロボットの位置情報（ポーズ）を受け取ることにより、ロボットが現在どの領域にいるのか、またはロボットに新たな目標位置を設定する際にその位置がどの領域に属するかを判断することができます。領域は「領域名」とその境界を形成する頂点座標（マップ座標系）を用いてポリゴンとして設定されます。設定された領域の可視化は、RVizで /region_markers トピックを受け取ることで行うことができます。

## 機能
* ロボットの現在位置や指定したポーズがどの領域に属するかを識別します。
* 各領域はポリゴンとして定義され、RVizで視覚化することが可能です。
* 地域名とその境界情報を基に、領域情報をトピックとして発行します。

## 前提条件
このパッケージを使用するためには、以下が必要です：

* ROS (Kinetic 以降のバージョン推奨)
* Python 2.7 または Python 3.5 以上
* shapely ライブラリ

## 領域情報などの設定
config/regions.yaml を参考に設定ファイルを作成し、実行時にそれを読み込むようにします。以下は設定の一例です：

```yaml
node:
  name: "region_checker"
topics:
  subscribe:
    pose: "/pre_target_pose"
  publish:
    current_region: "/current_region"
regions:
  - name: "Navigable Area"
    points:
      - [1.0, 1.0]
      - [5.0, 1.0]
      - [5.0, 5.0]
      - [1.0, 5.0]
```
regions属性には、複数の領域を与えることができます。個数に制限はありませんので、追加したいときは、さらに、nameとpointsタグを増やしてください。

## 実行方法
roslaunch region_checker region_checker.launch

## 可視化方法
RVizを開き、「Add」から「Marker」を選択し、/region_markers および /region_labels トピックを追加することで、地域の境界と名前のラベルを視覚的に確認できます。
