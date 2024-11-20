# Modelo Financiero

## Índice

1. [Introducción](#introducción)
2. [Objetivo](#objetivo)
3. [Instrumentos Financieros](#instrumentos-financieros)
4. [Indicadores](#indicadores)
    1. [ROI (Return On Investment)](#roi-return-on-investment)
    2. [IR (Índice de Rentabilidad)](#ir-índice-de-rentabilidad)
    3. [VNA (Valor Neto Actual)](#vna-valor-neto-actual)
    4. [TIR (Tasa Interna de Retorno)](#tir-tasa-interna-de-retorno)
    5. [Payback Period (Período de Recuperación)](#payback-period-período-de-recuperación)
5. [Resultados](#resultados)
6. [Bibliografia](#Bibliografia)

## Introducción

En esta sección se lleva a cabo un análisis financiero en el que se evalúan los modelos de VE (vehículos eléctricos) desde una perspectiva de rentabilidad, con el objetivo de identificar los prototipos de autos más eficientes que puedan generar un mejor rendimiento económico para la empresa.

Este análisis se compone de indicadores tales como:
- ROI (Return On Investment)
- IR (Índice de Rentabilidad)
- VNA (Valor Neto Actual)
- TIR (Tasa Interna de Retorno)
- Payback Period (Período de Recuperación)

El objeto de este estudio son los modelos de autos eléctricos encontrados en el Dataset «ElectricCarData_Clean».

Para la ejecución de este análisis, se utilizó información proveniente de fuentes como:
- NYC Department of Finance
- New York City Taxi and Limousine Commission
- U.S. Department of Energy
- New York DMV (Department of Motor Vehicles)

## Objetivo

- Realizar una proyección financiera a un periodo de 7 años para evaluar la viabilidad de un plan de negocios enfocado en ingresar al mercado de taxis dentro de la industria FHV (For Hire Vehicle) en la ciudad de Nueva York.

## Instrumentos Financieros

La piedra angular de este estudio es el flujo de caja, el cual proporciona la información necesaria para el cálculo de los indicadores previamente mencionados. Este instrumento financiero fue seleccionado porque permite visualizar el rendimiento monetario de un activo durante un periodo determinado (en este caso, 7 años). A lo largo de este periodo, se puede observar el comportamiento de variables como los ingresos, los costos operativos, el flujo neto y el flujo neto descontado.

## Indicadores

### ROI (Return On Investment)

<p align="center">
<img src="Images/ROI.png">
</p>

Es una métrica financiera utilizada para evaluar la rentabilidad de una inversión. El ROI muestra el rendimiento de una inversión en términos porcentuales. Es útil para comparar diferentes inversiones, evaluar su viabilidad económica y tomar decisiones informadas sobre dónde asignar recursos. Además, es de gran utilidad para inversores o gerentes a la hora de decidir si se debe proceder con un proyecto, basándose en su capacidad para generar beneficios sobre el capital invertido.

### IR (Índice de Rentabilidad)

<p align="center">
<img src="Images/IR.png"  style="max-width: 100%; height: auto;">
</p>

Es un indicador financiero que mide la rentabilidad de una inversión, similar al ROI, pero se calcula de manera diferente. Se usa para evaluar la relación entre los beneficios obtenidos y el costo de la inversión, considerando también el valor del dinero en el tiempo. El IR indica cuánto valor genera una inversión por cada dólar invertido. Si el valor del IR es mayor a 1, la inversión es rentable; si es menor a 1, la inversión no cubre su costo.

### VNA (Valor Neto Actual)

<p align="center">
<img src="Images/VNA.png"  style="max-width: 100%; height: auto;">
</p>

Es una herramienta financiera utilizada para evaluar la rentabilidad de una inversión considerando el valor del dinero en el tiempo. El VNA calcula la diferencia entre el valor actual de los ingresos futuros esperados y la inversión inicial. Se utiliza para determinar si un proyecto o inversión será rentable a lo largo del tiempo. Si el VNA es positivo, el proyecto es rentable, ya que indica que los ingresos futuros superan el costo de la inversión. Si el VNA es negativo, significa que el proyecto no cubre su costo y no generará valor.

### TIR (Tasa Interna de Retorno)

<p align="center">
<img src="Images/TIR.png"  style="max-width: 100%; height: auto;">
</p>

Es un indicador financiero que mide la rentabilidad de una inversión o proyecto. Representa la tasa de descuento que iguala el valor presente de los flujos de caja futuros de un proyecto con la inversión inicial. En otras palabras, la TIR es la tasa de interés a la cual el Valor Neto Actual (VNA) de los flujos de caja es igual a cero. Es utilizada para evaluar si un proyecto o inversión es viable económicamente.

### Payback Period (Período de Recuperación)

<p align="center">
<img src="Images/Payback.png"  style="max-width: 100%; height: auto;">
</p>

Es un indicador financiero que mide el tiempo que se tarda en recuperar la inversión inicial de un proyecto a través de sus flujos de caja futuros. En otras palabras, indica cuántos años se necesitarán para que la suma de los flujos de caja generados por el proyecto sea igual a la inversión inicial. El Payback Period es más útil para evaluar proyectos que requieren un retorno rápido de la inversión, lo que lo hace atractivo en contextos donde se priorizan los proyectos con menor riesgo a largo plazo.

## Resultados

Los resultados de este análisis se reflejan en las siguientes conclusiones:

- A pesar del alto precio de los vehículos eléctricos, estos son más rentables que un auto convencional a gasolina.
- La eficiencia (kWh/milla) es el aspecto que determina el desempeño rentable de los autos eléctricos, ya que permite que sus costos operativos sean menores en comparación con los de un auto convencional, además de los incentivos por parte del gobierno que se traducen en descuentos y exenciones de costos de trámites legales.
-  Incluir un vehículo convencional reduce el VAN en un 4.93%.
-   La inclusión de un vehículo convencional reduce la TIR en un 146.48%, indicando una disminución significativa en la rentabilidad relativa.
-   El ROI anual disminuye en un 164.44% al combinar vehículos convencionales, reflejando una reducción sustancial en la eficiencia financiera.
-   El tiempo de recuperación de la inversión aumenta en un 25% al incluir vehículos convencionales, demorando más el retorno del capital.
- Los modelos de autos que representan la mejor rentabilidad son «Mii Electric», «EQ forfour», «EQ fortwo coupe», «Me-Up!», «CITIGOe iV».
- Desde un punto de vista integral, involucrando la sustentabilidad, los modelos con mejor desempeño monetario y ambiental son «Mii Electric», «e-Up!» y «CITIGOe iV».

## Bibliografia

1. **Alternative Fuels Data Center (AFDC)**. "Electricity Benefits." U.S. Department of Energy, 2023. [https://afdc.energy.gov/fuels/electricity-benefits](https://afdc.energy.gov/fuels/electricity-benefits)
   
2. **Taxi and Limousine Commission (TLC)**. "Get a Vehicle License." City of New York, 2023. [https://www.nyc.gov/site/tlc/vehicles/get-a-vehicle-license.page](https://www.nyc.gov/site/tlc/vehicles/get-a-vehicle-license.page)
   
3. **Taxi and Limousine Commission (TLC)**. "Home." City of New York, 2023. [https://www.nyc.gov/site/tlc/index.page](https://www.nyc.gov/site/tlc/index.page)
   
4. **New York Department of Motor Vehicles (DMV)**. "Renew a Driver License." New York State, 2023. [https://dmv.ny.gov/driver-license/renew-a-driver-license](https://dmv.ny.gov/driver-license/renew-a-driver-license)
   
5. **New York City Department of Finance**. "Business Taxes and Information." City of New York, 2023. [https://www.nyc.gov/site/finance/business/business.page](https://www.nyc.gov/site/finance/business/business.page)
   
6. **New York Department of Motor Vehicles (DMV)**. "Register and Title a Vehicle." New York State, 2023. [https://dmv.ny.gov/registration/register-and-title-a-vehicle](https://dmv.ny.gov/registration/register-and-title-a-vehicle)
   
7. **Taxi and Limousine Commission (TLC)**. "Vehicle Insurance." City of New York, 2023. [https://www.nyc.gov/site/tlc/vehicles/vehicle-insurance.page](https://www.nyc.gov/site/tlc/vehicles/vehicle-insurance.page)
   
8. **Taxi and Limousine Commission (TLC)**. "FHV Corporations." City of New York, 2023. [https://www.nyc.gov/site/tlc/businesses/fhv-corporations.page](https://www.nyc.gov/site/tlc/businesses/fhv-corporations.page)
