"""
evaluate_model.py
Loads trained model, evaluates on test set, prints metrics, saves plot.
Run: python src/evaluate_model.py
"""
import os, sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEATURE_COLS = [
    'Hours_Studied', 'Attendance', 'Previous_Scores', 'Test_Score',
    'Project_Marks', 'Submission_Timeliness', 'Participation',
    'Extra_C', 'Backlogs',
    'engagement_feature', 'risk_feature', 'balance_feature', 'activeness_feature'
]


def evaluate():
    model_path = os.path.join(BASE_DIR, 'models', 'trained_model.pkl')
    data_path  = os.path.join(BASE_DIR, 'data', 'student_dataset_featured.csv')

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}. Run train_model.py first.")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found: {data_path}. Run feature_engineering.py first.")

    model = joblib.load(model_path)
    df    = pd.read_csv(data_path)
    print(f"Model: {type(model).__name__}")
    print(f"Data:  {df.shape}")

    X = df[FEATURE_COLS]
    y = df['Exam_Score']
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    y_pred = np.clip(model.predict(X_test), 0, 100)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2   = r2_score(y_test, y_pred)

    print("\n" + "=" * 40)
    print("  Model Evaluation Results")
    print("=" * 40)
    print(f"  Test samples : {len(y_test)}")
    print(f"  MAE          : {mae:.4f}")
    print(f"  RMSE         : {rmse:.4f}")
    print(f"  R2 Score     : {r2:.4f}")
    print("=" * 40)

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f'Evaluation - {type(model).__name__} (R2={r2:.3f})')

        axes[0].scatter(y_test, y_pred, alpha=0.4, s=18, color='#3b82f6')
        mn, mx = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
        axes[0].plot([mn, mx], [mn, mx], 'r--', lw=1.5)
        axes[0].set_xlabel('Actual'); axes[0].set_ylabel('Predicted')
        axes[0].set_title('Actual vs Predicted')

        residuals = y_test.values - y_pred
        axes[1].hist(residuals, bins=40, color='#8b5cf6', alpha=0.75)
        axes[1].axvline(0, color='red', linestyle='--', lw=1.5)
        axes[1].set_xlabel('Residual'); axes[1].set_title('Residual Distribution')

        plt.tight_layout()
        out = os.path.join(BASE_DIR, 'outputs', 'graphs', 'evaluation_plot.png')
        plt.savefig(out, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Plot saved: {out}")
    except ImportError:
        print("matplotlib not installed - skipping plot.")

    return {'MAE': round(mae, 4), 'RMSE': round(rmse, 4), 'R2': round(r2, 4)}


if __name__ == '__main__':
    evaluate()
