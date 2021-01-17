## 概要
ポートフォリオ最適化を行ってくれるプログラム。※未完


現状では、NASDAQの2020年以降の株価をパースし、DBに格納、マーコビッツの平均分散モデルにより、期待収益率が指定した値以上になるような制限のもと、分散最小化がなされる


現状NASDAQのすべての株でのポートフォリオ最小化であるが、個人が運用しようとした時数千の株を運用するのはあまり現実的ではないため、将来的には遺伝的アルゴリズム(https://github.com/physics-machinelearning/GenericAlgorithm)などを用いてn個の株の組み合わせの最適化を実現したい


また、最終的にはwebアプリにしたい


※log fileをdockerから取り出したいがデータ永続化する方法がわからず現状結果が取り出せない

## Usage
### 一番初め、テーブル作成からデータ収集、ポートフォリオ最適化まで一気に行いたいとき
- docker-compose run parserall

### 昨日からの一日分のデータのみ収集し、ポートフォリオ最適化を行いたいとき
- docker-compose run parseroneday

### データが溜まっている状態でポートフォリオ最適化のみ行いたい時
- docker-compose run optimization

## 参考にしたサイト
- https://qiita.com/matsxxx/items/0348af6ed1b1a2a2b84a
- https://qiita.com/yumaloop/items/d709cc9b43f18df70382