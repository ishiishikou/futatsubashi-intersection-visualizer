# Official plan notes

このノートは、公開資料から確認できる事項と、可視化上の解釈を分離するためのものです。

## 1号交差点の位置づけ

横浜市の工事説明資料では、三ツ境駅側からの既存道路と新設道路を接続するため、交差点形状を変更し、新たな横断歩道を整備する計画が示されています。

- 横浜市 2026年8月 工事説明会資料への案内ページ
  - https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/5.html
- 2026年8月資料
  - https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/5.files/0039_20260807.pdf
- 2025年7月資料にも「5-2. 交差点改良」として、三ツ境駅前からの道路と新設道路をつなげるため交差点形状を変更し、新たな横断歩道を作る旨が掲載されています。

ここでいう交差点改良は、県道45号（中原街道）の線路下本線を平面交差点化することを意味しません。現況OSMでは県道45号の該当区間が `tunnel=yes / layer=-1`、相模鉄道本線が `layer=1` と登録されており、本リポジトリではこの上下関係を保持して扱います。

## 2018年の信号パターン検討案

横浜市「第1期地区まちづくりニュース 第7号 別紙」（2018年5月18日発行）では、1号交差点について、歩行者・車両が交差点内で錯綜しないよう神奈川県警察と協議中として、次の信号パターン検討案が掲載されています。

1. 三ツ境下草柳線の直進・左折進行
2. 三ツ境下草柳線の右折（2方向）進行
3. 中原街道の側道 西側進行
4. 中原街道の側道 東側進行
5. 歩行者

資料には「今後の協議や実際の運用状況によって変更することがあります」と明記されています。このため、本リポジトリでこの5段階を描く場合は **2018年時点の検討案** と明示し、2026年時点の最終信号現示として扱いません。

- 過去号一覧
  - https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/news.html
- 第7号 PDF
  - https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/toshiseibi/jokyo/kukakuseiri/endouchiku/ikkichiku/news.files/0008_20190313.pdf

## 可視化ルール

- OSMで確認した現況形状は `Observed` とする。
- 横浜市の資料に明記された交差点改良・横断歩道・信号検討内容は `Official plan` とする。
- PDF画像そのものはコミットしない。
- 公式図を説明用に単純化したSVGは `Schematic interpretation` と明記する。
- 最終信号灯器の正確な位置、信号秒数、2026年時点の最終現示は、公式資料で確認できない限り描かない。
