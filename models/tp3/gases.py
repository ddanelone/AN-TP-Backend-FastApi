from pydantic import BaseModel, Field

class ParametrosIniciales(BaseModel):
    a: float = Field(..., gt=0, description="Límite inferior del intervalo")
    b: float = Field(..., gt=0, description="Límite superior del intervalo")
    tol: float = Field(1e-6, gt=0, description="Tolerancia para el método")
    max_iter: int = Field(50, gt=0, le=500, description="Máximo número de iteraciones")
