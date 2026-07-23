# 開発履歴

## 2026-07-24

### 左右トラックボールの微操作改善

- **目的**: 左右PMW3610で低速・微小移動が欠落し、右カーソルと左スクロールの細かな操作が段階的になる症状を改善する。
- **ブランチ**: `dev-main`
- **変更内容**:
  - `around_forty_db_right.overlay`: `motion-threshold` を `1` から `0` に変更し、±1カウントの移動を破棄しない。
  - `around_forty_db_right.conf`: `CONFIG_PMW3610_REPORT_INTERVAL_MIN` を `10ms` から `5ms` に短縮。
  - `around_forty_db_left.overlay`: `motion-threshold` を `1` から `0` に変更し、細かなスクロール入力を破棄しない。
  - `around_forty_db_left.conf`: `CONFIG_PMW3610_REPORT_INTERVAL_MIN` を `15ms` から `5ms` に短縮。
- **影響範囲**:
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right` / `around_forty_db_left`
  - split: 右Central / 左Peripheral。
  - レイヤー: 左右トラックボールを使う全レイヤー。
  - CPI、XY変換、スクロール変換、BLE設定、input listener構成は変更なし。

### GitHub Actions向けPMW3610依存の固定

- **目的**: ローカルパスに依存せず、GitHub ActionsのWest初期化で今回検証したPMW3610ドライバーを再現可能にする。
- **変更内容**:
  - `config/west.yml` の `zmk-pmw3610-driver` を、GitHubへ公開済みのコミット `8b605942880d46e3e2ab5b510fc47dd47f052440` に固定。
  - 参照先は `https://github.com/razilyis/zmk-pmw3610-driver`。
- **CI構成**:
  - workflow: `.github/workflows/build.yml`
  - reusable workflow: `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3.0`
  - board: `seeeduino_xiao_ble`
  - shield: `around_forty_db_right rgbled_adapter` / `around_forty_db_left rgbled_adapter`
  - West依存取得はreusable workflow内で実行。
  - `zmk-module-runtime-input-processor` は、ZMK v0.3互換かつローカル検証済みの `8103d0618856a099369f86e93b462ee987cf159a` に固定。
  - その他のcormoranモジュールもローカル検証済みコミットに固定し、`main`更新によるZMK v0.3 API不整合を防止。

### ZMK Keymap EditorへのBehavior公開

- **目的**: Westモジュール内の定義を直接読まないKeymap Editorでも、カスタムBehaviorを選択可能にする。
- **変更内容**:
  - `PMW3610 Inertia Toggle` をkeymap内に定義し、慣性スクロールON/OFF Behaviorを公開。
  - 既存のセンサー回転Behaviorに `SCROLL_UP_DOWN` ラベルを追加し、スクロール方向Behaviorを公開。
- **影響範囲**:
  - `config/around_forty_db.keymap` のBehaviorメタデータのみ。
  - 既存のキー配置および実行時動作は変更なし。
