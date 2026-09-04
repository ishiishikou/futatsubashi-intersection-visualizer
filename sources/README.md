# Sources

このディレクトリには第三者資料そのものを保存せず、参照先・権威・用途・優先度を記録します。

## 参照元の正式な登録先

- [source-register.md](source-register.md)
  - 今回の工事・交差点構造を検討する際に参照すべき一次資料、地図資料、過去資料、交通信号・道路設計の方法論資料を登録しています。
  - 新しい公式資料を使う前に、まずこの一覧へ追加します。

## 調査手順

- [../docs/investigation-plan.md](../docs/investigation-plan.md)
  - 道路技術者の進め方にならい、現況図確定 → 高さ分離 → 道路ID付与 → 公式計画の位置合わせ → 方向別交通流 → 信号制御、の順に検討します。

## 運用ルール

- 横浜市PDF、国土地理院資料等の原本画像を恒久的にリポジトリへ再掲しません。
- Google Mapsのスクリーンショットやそのトレースをコミットしません。
- OpenStreetMapは補助・照合用とし、数十mスケールの現況形状は横浜市道路台帳/Rマッピー等を優先します。
- SVGへ反映する計画道路・交通島・横断歩道・信号関連情報には、根拠資料またはprovenance IDを付けます。
- 公開資料で確認できない車線、信号灯器位置、信号現示、信号秒数等は推定で埋めず `Unknown` とします。
- 情報は `Observed` / `Official plan` / `Derived` / `Interpretation` / `Unknown` に分けて扱います。

## OpenStreetMap attribution

OpenStreetMap由来の地理データを成果物に使用する場合は、必要な帰属表示を行います。

- © OpenStreetMap contributors
- Open Database License (ODbL)
