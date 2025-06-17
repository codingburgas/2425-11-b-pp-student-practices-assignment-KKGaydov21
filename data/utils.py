import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(data):
    """
    Зарежда и предварително обработва Cancer dataset.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Raw cancer data
        
    Returns:
    --------
    tuple
        (X, y, feature_names, scaler)
        X : array-like, shape (n_samples, n_features) - Стандартизирани характеристики
        y : array-like, shape (n_samples,) - Бинарни етикети (0/1)
        feature_names : list - Имена на характеристиките
        scaler : StandardScaler - Обучен scaler за денормализация
    """
    
    # Създаваме копие за безопасна работа
    df = data.copy()
    
    # Проверяваме задължителните колони
    if 'diagnosis' not in df.columns:
        raise ValueError("Dataset трябва да съдържа колона 'diagnosis'")
    
    # Преобразуваме diagnosis в бинарни стойности
    # M (Malignant) = 1, B (Benign) = 0
    diagnosis_map = {'M': 1, 'B': 0}
    y = df['diagnosis'].map(diagnosis_map)
    
    if y.isnull().any():
        raise ValueError("Diagnosis колоната съдържа неразпознати стойности. Очакват се 'M' или 'B'.")
    
    # Премахваме нечислови колони
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    # Премахваме id колони ако съществуват
    id_columns = [col for col in df.columns if 'id' in col.lower()]
    numeric_columns = [col for col in numeric_columns if col not in id_columns]
    
    if len(numeric_columns) == 0:
        raise ValueError("Не са намерени числови характеристики в dataset-а")
    
    # Извличаме характеристиките
    X = df[numeric_columns].values
    feature_names = list(numeric_columns)
    
    # Проверяваме за липсващи стойности
    if np.isnan(X).any():
        print("⚠️  Внимание: Намерени са липсващи стойности. Заместват се със средната стойност.")
        # Заместваме NaN със средната стойност
        from sklearn.impute import SimpleImputer
        imputer = SimpleImputer(strategy='mean')
        X = imputer.fit_transform(X)
    
    # Стандартизираме данните
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    print(f"✅ Данните са заредени успешно:")
    print(f"   - Записи: {X.shape[0]}")
    print(f"   - Характеристики: {X.shape[1]}")
    print(f"   - Злокачествени случаи: {y.sum()} ({y.mean()*100:.1f}%)")
    print(f"   - Доброкачествени случаи: {len(y) - y.sum()} ({(1-y.mean())*100:.1f}%)")
    
    return X, y.values, feature_names, scaler

def describe_dataset(data):
    """
    Предоставя детайлно описание на dataset-а.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Cancer dataset
        
    Returns:
    --------
    dict
        Речник със статистики за dataset-а
    """
    stats = {}
    
    # Основна информация
    stats['shape'] = data.shape
    stats['columns'] = data.columns.tolist()
    stats['dtypes'] = data.dtypes.to_dict()
    
    # Информация за diagnosis
    if 'diagnosis' in data.columns:
        diagnosis_counts = data['diagnosis'].value_counts()
        stats['diagnosis_distribution'] = diagnosis_counts.to_dict()
        stats['class_balance'] = diagnosis_counts / len(data)
    
    # Статистики за числовите колони
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        stats['numeric_summary'] = data[numeric_cols].describe()
        stats['missing_values'] = data[numeric_cols].isnull().sum().to_dict()
        stats['correlations'] = data[numeric_cols].corr()
    
    return stats

def create_sample_data_explanation():
    """
    Създава обяснение за структурата на данните.
    
    Returns:
    --------
    str
        Форматиран текст с обяснение
    """
    explanation = """
    📊 **Структура на Cancer Dataset:**
    
    **Основни колони:**
    - `diagnosis`: Диагноза (M = Злокачествен, B = Доброкачествен)
    - Числови характеристики на туморите:
    
    **Категории характеристики:**
    1. **Radius** - Радиус (разстояние от центъра до точките на периметъра)
    2. **Texture** - Текстура (стандартно отклонение на стойностите в сивата скала)
    3. **Perimeter** - Периметър
    4. **Area** - Площ
    5. **Smoothness** - Гладкост (локална вариация в дължините на радиуса)
    6. **Compactness** - Компактност (периметър² / площ - 1.0)
    7. **Concavity** - Вдлъбнатост (сериозност на вдлъбнатите части на контура)
    8. **Concave points** - Вдлъбнати точки (брой вдлъбнати части на контура)
    9. **Symmetry** - Симетрия
    10. **Fractal dimension** - Фрактална размерност
    
    **За всяка характеристика се изчисляват:**
    - Mean (средна стойност)
    - Standard Error (стандартна грешка)
    - Worst (най-лошата стойност)
    
    **Общо: 30 характеристики + diagnosis**
    """
    
    return explanation

def validate_model_performance(y_true, y_pred, y_pred_proba=None):
    """
    Валидира производителността на модела и връща детайлни метрики.
    
    Parameters:
    -----------
    y_true : array-like
        Истински етикети
    y_pred : array-like
        Предсказани етикети
    y_pred_proba : array-like, optional
        Предсказани вероятности
        
    Returns:
    --------
    dict
        Речник с метрики за производителност
    """
    from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                                f1_score, confusion_matrix, classification_report,
                                roc_auc_score, roc_curve)
    
    metrics = {}
    
    # Основни метрики
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['precision'] = precision_score(y_true, y_pred)
    metrics['recall'] = recall_score(y_true, y_pred)
    metrics['f1_score'] = f1_score(y_true, y_pred)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics['confusion_matrix'] = cm
    metrics['true_negatives'] = cm[0, 0]
    metrics['false_positives'] = cm[0, 1]
    metrics['false_negatives'] = cm[1, 0]
    metrics['true_positives'] = cm[1, 1]
    
    # Специфичност и чувствителност
    metrics['sensitivity'] = metrics['recall']  # True Positive Rate
    metrics['specificity'] = cm[0, 0] / (cm[0, 0] + cm[0, 1])  # True Negative Rate
    
    # ROC метрики ако са предоставени вероятности
    if y_pred_proba is not None:
        metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba)
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        metrics['roc_curve'] = {'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds}
    
    # Класификационен отчет
    metrics['classification_report'] = classification_report(y_true, y_pred, output_dict=True)
    
    return metrics

def generate_medical_interpretation(metrics, feature_importance=None):
    """
    Генерира медицинска интерпретация на резултатите.
    
    Parameters:
    -----------
    metrics : dict
        Метрики за производителност
    feature_importance : dict, optional
        Важност на характеристиките
        
    Returns:
    --------
    str
        Медицинска интерпретация
    """
    interpretation = f"""
    🏥 **Медицинска интерпретация на резултатите:**
    
    **Общи показатели:**
    - Точност: {metrics['accuracy']:.1%} (процент правилни диагнози)
    - Чувствителност: {metrics['sensitivity']:.1%} (процент открити злокачествени случаи)
    - Специфичност: {metrics['specificity']:.1%} (процент правилно идентифицирани доброкачествени случаи)
    
    **Клинично значение:**
    - True Positives: {metrics['true_positives']} (правилно открити злокачествени)
    - False Negatives: {metrics['false_negatives']} (пропуснати злокачествени - ОПАСНО!)
    - False Positives: {metrics['false_positives']} (погрешно диагностицирани като злокачествени)
    - True Negatives: {metrics['true_negatives']} (правилно идентифицирани доброкачествени)
    
    **Медицински съвети:**
    """
    
    # Съвети базирани на резултатите
    if metrics['sensitivity'] < 0.9:
        interpretation += "\n⚠️  ВНИМАНИЕ: Ниска чувствителност! Моделът може да пропусне злокачествени случаи."
    
    if metrics['specificity'] < 0.8:
        interpretation += "\n⚠️  ВНИМАНИЕ: Ниска специфичност! Много доброкачествени случаи се диагностицират като злокачествени."
    
    if metrics['false_negatives'] > 0:
        interpretation += f"\n🔴 Критично: {metrics['false_negatives']} злокачествени случая са пропуснати!"
    
    if feature_importance:
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        interpretation += f"\n\n**Най-важни характеристики за диагнозата:**"
        for i, (feature, importance) in enumerate(top_features, 1):
            interpretation += f"\n{i}. {feature}: {importance:.4f}"
    
    interpretation += f"""
    
    **Препоръки за клинично използване:**
    - Моделът трябва да се използва като помощно средство, не като замяна на лекаря
    - При съмнение винаги да се прави допълнителна диагностика
    - Редовно да се актуализира с нови данни
    """
    
    return interpretation
