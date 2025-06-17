import numpy as np

class LogisticRegression:
    """
    Имплементация на логистична регресия от нулата за образователни цели.
    Демонстрира всички ключови концепции: sigmoid, loss function, gradient descent.
    """
    
    def __init__(self, learning_rate=0.01, max_iterations=1000, tolerance=1e-6):
        """
        Инициализация на модела.
        
        Parameters:
        -----------
        learning_rate : float
            Скорост на обучение (α)
        max_iterations : int
            Максимален брой итерации
        tolerance : float
            Толеранс за конвергенция
        """
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.weights = None
        self.bias = None
        self.losses = []
    
    def _add_bias(self, X):
        """Добавя bias колона към матрицата X."""
        return np.column_stack([np.ones(X.shape[0]), X])
    
    def _sigmoid(self, z):
        """
        Sigmoid функция: σ(z) = 1 / (1 + e^(-z))
        
        Parameters:
        -----------
        z : array-like
            Линейна комбинация (weighted sum)
            
        Returns:
        --------
        array-like
            Sigmoid стойности между 0 и 1
        """
        # Клипиране за численна стабилност
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))
    
    def _linear_combination(self, X):
        """
        Изчислява линейната комбинация z = w₀ + w₁x₁ + ... + wₙxₙ
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
            Входни характеристики
            
        Returns:
        --------
        array-like
            Линейни комбинации
        """
        return X @ self.weights
    
    def _binary_cross_entropy_loss(self, y_true, y_pred):
        """
        Binary Cross-Entropy Loss Function:
        L = -1/m * Σ[y*log(ŷ) + (1-y)*log(1-ŷ)]
        
        Parameters:
        -----------
        y_true : array-like
            Истински стойности (0 или 1)
        y_pred : array-like
            Предсказани вероятности (0 до 1)
            
        Returns:
        --------
        float
            Loss стойност
        """
        # Клипиране за численна стабилност
        y_pred = np.clip(y_pred, 1e-15, 1 - 1e-15)
        
        m = len(y_true)
        loss = -1/m * np.sum(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        return loss
    
    def _compute_gradients(self, X, y_true, y_pred):
        """
        Изчислява градиентите за всички тежести.
        
        Градиентите са:
        ∂L/∂w = 1/m * X^T * (ŷ - y)
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features + 1)
            Входни данни с bias колона
        y_true : array-like
            Истински стойности
        y_pred : array-like
            Предсказани вероятности
            
        Returns:
        --------
        array-like
            Градиенти за всички тежести
        """
        m = X.shape[0]
        gradients = 1/m * X.T @ (y_pred - y_true)
        return gradients
    
    def fit(self, X, y):
        """
        Обучава модела използвайки Gradient Descent.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
            Тренировъчни данни
        y : array-like, shape (n_samples,)
            Целеви стойности (0 или 1)
            
        Returns:
        --------
        list
            История на loss стойностите
        """
        # Добавяме bias колона
        X_with_bias = self._add_bias(X)
        
        # Инициализираме тежестите произволно
        n_features = X_with_bias.shape[1]
        self.weights = np.random.normal(0, 0.01, n_features)
        
        self.losses = []
        
        for iteration in range(self.max_iterations):
            # Forward pass
            # 1. Изчисляваме линейната комбинация
            z = self._linear_combination(X_with_bias)
            
            # 2. Прилагаме sigmoid функция
            y_pred = self._sigmoid(z)
            
            # 3. Изчисляваме загубата
            loss = self._binary_cross_entropy_loss(y, y_pred)
            self.losses.append(loss)
            
            # Backward pass
            # 4. Изчисляваме градиентите
            gradients = self._compute_gradients(X_with_bias, y, y_pred)
            
            # 5. Обновяваме тежестите
            new_weights = self.weights - self.learning_rate * gradients
            
            # Проверяваме за конвергенция
            if np.allclose(self.weights, new_weights, atol=self.tolerance):
                print(f"Конвергенция достигната на итерация {iteration}")
                break
                
            self.weights = new_weights
            
            # Показваме прогрес на всеки 100 итерации
            if iteration % 100 == 0:
                print(f"Итерация {iteration}: Loss = {loss:.6f}")
        
        return self.losses
    
    def predict_proba(self, X):
        """
        Предсказва вероятности.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
            Данни за предсказание
            
        Returns:
        --------
        array-like
            Вероятности за клас 1
        """
        if self.weights is None:
            raise ValueError("Моделът не е обучен. Извикайте fit() първо.")
        
        X_with_bias = self._add_bias(X)
        z = self._linear_combination(X_with_bias)
        return self._sigmoid(z)
    
    def predict(self, X, threshold=0.5):
        """
        Предсказва класове използвайки threshold.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
            Данни за предсказание
        threshold : float
            Праг за класификация (по подразбиране 0.5)
            
        Returns:
        --------
        array-like
            Предсказани класове (0 или 1)
        """
        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int)
    
    def get_weights(self):
        """
        Връща научените тежести.
        
        Returns:
        --------
        dict
            Речник с bias и weights
        """
        if self.weights is None:
            return None
        
        return {
            'bias': self.weights[0],
            'weights': self.weights[1:]
        }
    
    def decision_function(self, X):
        """
        Връща стойностите на decision function (z = w^T * x + b).
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
            Входни данни
            
        Returns:
        --------
        array-like
            Decision function стойности
        """
        if self.weights is None:
            raise ValueError("Моделът не е обучен. Извикайте fit() първо.")
        
        X_with_bias = self._add_bias(X)
        return self._linear_combination(X_with_bias)
    
    def feature_importance(self, feature_names=None):
        """
        Връща важността на характеристиките (абсолютни стойности на тежестите).
        
        Parameters:
        -----------
        feature_names : list, optional
            Имена на характеристиките
            
        Returns:
        --------
        dict
            Важност на характеристиките
        """
        if self.weights is None:
            raise ValueError("Моделът не е обучен. Извикайте fit() първо.")
        
        weights = self.weights[1:]  # Без bias
        importances = np.abs(weights)
        
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(weights))]
        
        return dict(zip(feature_names, importances))
