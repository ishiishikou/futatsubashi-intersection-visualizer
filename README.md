# futatsubashi-intersection-visualizer

横浜市瀬谷区・二ツ橋周辺の1号交差点について、**立体交差を平面交差と誤認しないこと**を最優先に、公開データから道路構造と信号計画を可視化する検証リポジトリです。

## まず見る図

### 1. 現況の上下関係

![交差点周辺の現況](docs/generated/03-local-focus.png)

OpenStreetMap から取得した現況形状を使用しています。

- 中原街道（県道45号）の該当区間: `tunnel=yes`, `layer=-1`
- 相模鉄道本線: `layer=1`
- 三ツ境下草柳線の新設区間: `highway=construction`

したがって、県道45号の線路下本線と、地上で信号制御される道路は同一平面ではありません。

### 2. レイヤーを分解して確認

![上下レイヤーの分解](docs/generated/04-layer-exploded.png)

同じ場所・同じ縮尺を「地上」「県道45号アンダーパス」「相鉄線」「重ね合わせ」に分離しています。

### 3. 2018年に公表された信号パターン検討案

![2018年信号パターン検討案](docs/generated/05-signal-phases-2018.png)

横浜市「第1期地区まちづくりニュース 第7号 別紙」に掲載された検討案を、説明用の模式図として再構成しています。

1. 三ツ境下草柳線の直進・左折
2. 三ツ境下草柳線の右折（2方向）
3. 中原街道の側道 西側
4. 中原街道の側道 東側
5. 歩行者

**これは2018年時点の検討案であり、2026年の最終信号現示・灯器配置を示すものではありません。**

## このリポジトリで区別する情報

- **Observed**: OpenStreetMap 等の公開地理データから機械的に確認できる現況
- **Official plan**: 横浜市等の公式資料に明記された計画内容
- **Schematic interpretation**: 上記を理解しやすくするために当リポジトリで作成した模式図

正確な最終信号灯器位置、信号秒数、最終現示については、公式資料で確認できない限り推測して描きません。

## 公開データの扱い

このリポジトリは public を前提にしています。Google Maps のスクリーンショットやそのトレース、個人情報、認証情報、横浜市PDFの画像そのものはコミットしません。詳細は [PUBLIC_DATA_POLICY.md](PUBLIC_DATA_POLICY.md) を参照してください。

地理データ由来の図には `© OpenStreetMap contributors (ODbL)` を表示しています。

## 公式資料

参照元と、どの情報を反映したかは [sources/README.md](sources/README.md) および [docs/official-plan-notes.md](docs/official-plan-notes.md) に整理しています。

## 再生成

GitHub Actions が公開OSMデータからSVGを生成し、PNGへ決定論的にレンダリングした後、SVGの構造検査を実行します。SVGを編集可能なmasterとし、PNGはレビュー用成果物として扱います。
