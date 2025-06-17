import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def create_sigmoid_plot():
    """
    Създава интерактивна визуализация на sigmoid функцията.
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Интерактивен график на sigmoid функцията
    """
    # Създаваме стойности за z
    z = np.linspace(-10, 10, 1000)
    sigmoid_z = 1 / (1 + np.exp(-z))
    
    fig = go.Figure()
    
    # Добавяме sigmoid кривата
    fig.add_trace(go.Scatter(
        x=z,
        y=sigmoid_z,
        mode='lines',
        name='σ(z) = 1/(1 + e^(-z))',
        line=dict(color='blue', width=3),
        hovertemplate='z: %{x:.2f}<br>σ(z): %{y:.4f}<extra></extra>'
    ))
    
    # Добавяме важни точки
    important_points_z = [-2, -1, 0, 1, 2]
    important_points_sigmoid = [1 / (1 + np.exp(-z_val)) for z_val in important_points_z]
    
    fig.add_trace(go.Scatter(
        x=important_points_z,
        y=important_points_sigmoid,
        mode='markers',
        name='Важни точки',
        marker=dict(color='red', size=8),
        hovertemplate='z: %{x}<br>σ(z): %{y:.4f}<extra></extra>'
    ))
    
    # Добавяме хоризонтални линии за threshold
    fig.add_hline(y=0.5, line_dash="dash", line_color="green", 
                  annotation_text="Threshold = 0.5", annotation_position="right")
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    fig.add_hline(y=1, line_dash="dot", line_color="gray", opacity=0.5)
    
    # Добавяме вертикална линия при z=0
    fig.add_vline(x=0, line_dash="dot", line_color="gray", opacity=0.5)
    
    # Настройваме layout
    fig.update_layout(
        title={
            'text': 'Sigmoid функция σ(z) = 1/(1 + e^(-z))',
            'x': 0.5,
            'font': {'size': 16}
        },
        xaxis_title='z (Линейна комбинация)',
        yaxis_title='σ(z) (Вероятност)',
        xaxis=dict(range=[-10, 10], gridcolor='lightgray'),
        yaxis=dict(range=[-0.1, 1.1], gridcolor='lightgray'),
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(x=0.02, y=0.98),
        width=800,
        height=500
    )
    
    # Добавяме текстови аннотации
    fig.add_annotation(
        x=-5, y=0.05,
        text="Клас 0<br>(Доброкачествен)",
        showarrow=False,
        font=dict(color="blue", size=12),
        bgcolor="lightblue",
        opacity=0.8
    )
    
    fig.add_annotation(
        x=5, y=0.95,
        text="Клас 1<br>(Злокачествен)",
        showarrow=False,
        font=dict(color="red", size=12),
        bgcolor="lightcoral",
        opacity=0.8
    )
    
    return fig

def create_decision_boundary_plot(X, y, model):
    """
    Създава визуализация на decision boundary.
    
    Parameters:
    -----------
    X : array-like, shape (n_samples, 2)
        2D данни за визуализация
    y : array-like, shape (n_samples,)
        Етикети на класовете
    model : LogisticRegression
        Обучен модел
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Интерактивен график с decision boundary
    """
    fig = go.Figure()
    
    # Разделяме данните по класове
    X_class_0 = X[y == 0]
    X_class_1 = X[y == 1]
    
    # Добавяме точките за всеки клас
    fig.add_trace(go.Scatter(
        x=X_class_0[:, 0],
        y=X_class_0[:, 1],
        mode='markers',
        name='Доброкачествен (0)',
        marker=dict(color='blue', size=6, opacity=0.7),
        hovertemplate='PC1: %{x:.2f}<br>PC2: %{y:.2f}<br>Клас: Доброкачествен<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=X_class_1[:, 0],
        y=X_class_1[:, 1],
        mode='markers',
        name='Злокачествен (1)',
        marker=dict(color='red', size=6, opacity=0.7),
        hovertemplate='PC1: %{x:.2f}<br>PC2: %{y:.2f}<br>Клас: Злокачествен<extra></extra>'
    ))
    
    # Създаваме мрежа за decision boundary
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 100),
        np.linspace(y_min, y_max, 100)
    )
    
    # Предсказваме вероятностите за мрежата
    mesh_points = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict_proba(mesh_points)
    Z = Z.reshape(xx.shape)
    
    # Добавяме contour plot за вероятностите
    fig.add_trace(go.Contour(
        x=np.linspace(x_min, x_max, 100),
        y=np.linspace(y_min, y_max, 100),
        z=Z,
        colorscale='RdYlBu_r',
        opacity=0.3,
        showscale=True,
        colorbar=dict(title="Вероятност<br>за клас 1"),
        contours=dict(
            start=0,
            end=1,
            size=0.1,
        ),
        hovertemplate='PC1: %{x:.2f}<br>PC2: %{y:.2f}<br>Вероятност: %{z:.3f}<extra></extra>',
        name='Вероятност'
    ))
    
    # Добавяме decision boundary (вероятност = 0.5)
    fig.add_trace(go.Contour(
        x=np.linspace(x_min, x_max, 100),
        y=np.linspace(y_min, y_max, 100),
        z=Z,
        contours=dict(
            start=0.5,
            end=0.5,
            size=0.1,
            coloring='lines'
        ),
        line=dict(color='black', width=3),
        showscale=False,
        name='Decision Boundary',
        hovertemplate='Decision Boundary<br>Вероятност = 0.5<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Граница на решение (Decision Boundary)',
            'x': 0.5,
            'font': {'size': 16}
        },
        xaxis_title='Първа главна компонента (PC1)',
        yaxis_title='Втора главна компонента (PC2)',
        plot_bgcolor='white',
        showlegend=True,
        width=800,
        height=600
    )
    
    return fig

def create_loss_plot():
    """
    Създава визуализация на Binary Cross-Entropy loss функцията.
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Интерактивен график на loss функцията
    """
    # Създаваме стойности за предсказаните вероятности
    y_pred = np.linspace(0.001, 0.999, 1000)
    
    # Изчисляваме loss за y_true = 1 и y_true = 0
    loss_y1 = -np.log(y_pred)  # Когато y_true = 1
    loss_y0 = -np.log(1 - y_pred)  # Когато y_true = 0
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Когато y = 1 (Злокачествен)', 'Когато y = 0 (Доброкачествен)'],
        horizontal_spacing=0.1
    )
    
    # График за y_true = 1
    fig.add_trace(
        go.Scatter(
            x=y_pred,
            y=loss_y1,
            mode='lines',
            name='Loss = -log(ŷ)',
            line=dict(color='red', width=3),
            hovertemplate='ŷ: %{x:.3f}<br>Loss: %{y:.3f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # График за y_true = 0
    fig.add_trace(
        go.Scatter(
            x=y_pred,
            y=loss_y0,
            mode='lines',
            name='Loss = -log(1-ŷ)',
            line=dict(color='blue', width=3),
            hovertemplate='ŷ: %{x:.3f}<br>Loss: %{y:.3f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Добавяме важни точки
    important_probs = [0.1, 0.5, 0.9]
    
    for prob in important_probs:
        # За y_true = 1
        loss_1 = -np.log(prob)
        fig.add_trace(
            go.Scatter(
                x=[prob], y=[loss_1],
                mode='markers',
                marker=dict(color='red', size=8),
                showlegend=False,
                hovertemplate=f'ŷ: {prob}<br>Loss: {loss_1:.3f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # За y_true = 0
        loss_0 = -np.log(1 - prob)
        fig.add_trace(
            go.Scatter(
                x=[prob], y=[loss_0],
                mode='markers',
                marker=dict(color='blue', size=8),
                showlegend=False,
                hovertemplate=f'ŷ: {prob}<br>Loss: {loss_0:.3f}<extra></extra>'
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title={
            'text': 'Binary Cross-Entropy Loss Function',
            'x': 0.5,
            'font': {'size': 16}
        },
        height=500,
        showlegend=True
    )
    
    # Настройваме осите
    fig.update_xaxes(title_text="Предсказана вероятност (ŷ)", range=[0, 1])
    fig.update_yaxes(title_text="Loss", range=[0, 5])
    
    # Добавяме аннотации
    fig.add_annotation(
        x=0.9, y=2.5,
        text="Добро предсказание<br>(ниска загуба)",
        showarrow=True,
        arrowhead=2,
        arrowcolor="green",
        row=1, col=1
    )
    
    fig.add_annotation(
        x=0.1, y=2.5,
        text="Добро предсказание<br>(ниска загуба)",
        showarrow=True,
        arrowhead=2,
        arrowcolor="green",
        row=1, col=2
    )
    
    return fig

def create_3d_surface_plot(X, y, model, feature_names):
    """
    Създава 3D surface plot за визуализация на decision surface.
    
    Parameters:
    -----------
    X : array-like, shape (n_samples, 2)
        2D данни
    y : array-like, shape (n_samples,)
        Етикети
    model : LogisticRegression
        Обучен модел
    feature_names : list
        Имена на характеристиките
        
    Returns:
    --------
    plotly.graph_objects.Figure
        3D интерактивен график
    """
    # Създаваме мрежа
    x_range = np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 50)
    y_range = np.linspace(X[:, 1].min() - 1, X[:, 1].max() + 1, 50)
    xx, yy = np.meshgrid(x_range, y_range)
    
    # Предсказваме вероятности
    mesh_points = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict_proba(mesh_points)
    Z = Z.reshape(xx.shape)
    
    fig = go.Figure()
    
    # Добавяме surface
    fig.add_trace(go.Surface(
        x=xx,
        y=yy,
        z=Z,
        colorscale='RdYlBu_r',
        opacity=0.8,
        name='Вероятностна повърхност'
    ))
    
    # Добавяме данните като точки
    colors = ['blue' if label == 0 else 'red' for label in y]
    
    fig.add_trace(go.Scatter3d(
        x=X[:, 0],
        y=X[:, 1],
        z=np.zeros(len(X)),  # Проектираме на z=0
        mode='markers',
        marker=dict(
            size=5,
            color=colors,
            opacity=0.8
        ),
        name='Данни'
    ))
    
    fig.update_layout(
        title='3D Визуализация на Decision Surface',
        scene=dict(
            xaxis_title=feature_names[0] if len(feature_names) > 0 else 'Feature 1',
            yaxis_title=feature_names[1] if len(feature_names) > 1 else 'Feature 2',
            zaxis_title='Вероятност'
        ),
        width=800,
        height=600
    )
    
    return fig

def create_feature_importance_plot(model, feature_names):
    """
    Създава барChart за важността на характеристиките.
    
    Parameters:
    -----------
    model : LogisticRegression
        Обучен модел
    feature_names : list
        Имена на характеристиките
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Bar chart на важността
    """
    importance_dict = model.feature_importance(feature_names)
    
    # Сортираме по важност
    sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
    features, importances = zip(*sorted_importance)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=list(features),
        y=list(importances),
        marker_color='steelblue',
        hovertemplate='%{x}<br>Важност: %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Важност на характеристиките (|Тегло|)',
        xaxis_title='Характеристики',
        yaxis_title='Абсолютна стойност на теглото',
        xaxis_tickangle=-45,
        height=500
    )
    
    return fig
