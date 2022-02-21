# InfoPave-Analyzer

## Introducción

## Funcionamiento

## Módulos

### main.py

Es el módulo principal del sistema. Ordena la conversión de los archivos a un formato reconocible, y unifica los valores en una tabla maestra.

### xls2csv.py

Este módulo realiza la conversión de los ficheros en formato Excel (extensión `.xlsx`) a tablas con valores separados por comas (extensión `.csv`).

Tablas LTPP reconocidas por el módulo:

| Nombre de la hoja Excel   | Parameter               | Code      |
|---------------------------|-------------------------|-----------|
| `MON_HSS_PROFILE_SECTION` | Roughness (IRI)         | `IRI`     |
| `MON_DEFL_DROP_DATA`      | Deflection              | `DEF`     |
| `MON_FRICTION`            | Friction                | `SKN`     |
| `TRF_ESAL_INPUTS_SUMMARY` | Structural Number       | `SNU`     |
| `EXPERIMENT_SECTION`      | Pavement Age            | `Pa`      |
| `CLM_VWS_PRECIP_ANNUAL`   | Precipitation (annual)  | `WMS_PRA` |
| `CLM_VWS_PRECIP_MONTH`    | Precipitation (monthly) | `WMS_PRM` |
| `CLM_VWS_TEMP_ANNUAL`     | Temperature (annual)    | `WMS_TEA` |
| `CLM_VWS_TEMP_MONTH`      | Temperature (monthly)   | `WMS_TEM` |
| `CLM_VWS_WIND_ANNUAL`     | Wind speed (annual)     | `WMS_WIA` |
| `CLM_VWS_WIND_MONTH`      | Wind speed (monthly)    | `WMS_WIM` |
| `CLM_VWS_HUMIDITY_ANNUAL` | Humidity (annual)       | `WMS_HUA` |
| `CLM_VWS_HUMIDITY_MONTH`  | Humidity (monthly)      | `WMS_HUM` |

