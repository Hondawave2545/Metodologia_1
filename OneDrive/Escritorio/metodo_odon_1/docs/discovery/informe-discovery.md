---
: "Informe de Discovery: sistemas de gestión de turnos odontológicos en Argentina"
---

# Informe de Discovery

## Sistema de gestión de turnos y agenda de pacientes para consultorios odontológicos

| | |
|---|---|
| **Materia** | Metodología I — Tecnicatura Universitaria en Programación |
| **Integrantes** | Yoselie Aquino |
| **Fecha de consulta de fuentes** | 2026-10-15 |
| **Repositorio** | https://github.com/Hondawave2545/Metodologia_1.git |



## Resumen ejecutivo

**Qué se investigó.** Se relevaron 15 sistemas de gestión odontológica y de agenda de turnos con presencia en Argentina o Latinoamérica, comparando reserva online, recordatorios, funciones clínicas, administración, integraciones, seguridad y modelo comercial. Cada celda distingue entre lo **comprobado** (la función se describe o se muestra en la página oficial), lo **declarado** (aparece como mención o extracto sin detalle) y lo **no evidenciado**. No se probó ningún producto ni se contactó a ningún proveedor.

**Principales hallazgos.**

- Siete sistemas tienen evidencia suficiente para puntuarse: DentalSoft (4,50), ClinIA (4,40), Nubimed (4,10), AgendaPro (4,06), Dentalink (3,85), Dentidesk (3,17) y Nimbo (2,94). Los dos primeros están prácticamente empatados.
- La agenda multiprofesional, la reserva online y los recordatorios automáticos ya son estándar. Competir solo con esas funciones no diferencia.
- Los competidores locales (DentalSoft, ClinIA) combinan agenda con obras sociales, WhatsApp y, en el caso de ClinIA, facturación ARCA. Quedan vacíos en transparencia de precios, en recordatorios automáticos fuera de los planes altos y en gestión explícita de sillones.
- Los puntajes surgen de páginas comerciales: son hipótesis que deben validarse con demos y entrevistas.

**MVP recomendado.** Un núcleo de **agenda confiable** para consultorios de uno a cinco profesionales: turnos con prevención atómica de solapamientos por profesional y por sillón, estados operativos, roles y trazabilidad; con recordatorios por WhatsApp como puerta de decisión previa al piloto. Quedan fuera la historia clínica, el odontograma, la facturación y las obras sociales. Antes de congelar el alcance debe decidirse, con usuarios, si un odontograma básico es condición para adoptar el sistema.

\newpage

## A. Tabla comparativa de 15 sistemas

Ordenada por relevancia para Argentina (producto local o con sitio y oferta para Argentina primero; luego Latinoamérica e internacionales).

**Criterio de evidencia.** *Comprobado*: la página oficial consultada describe o muestra la función con detalle. *Declarado*: la función aparece mencionada (lista de módulos, extracto, blog del proveedor o ficha de un marketplace) sin detalle verificable. *No evidenciado*: no hay respaldo público en las fuentes consultadas. Las cifras de resultados que publican los proveedores (por ejemplo, "menos ausencias") son afirmaciones comerciales y no se usan para puntuar.

| # | Producto / Proveedor | País · Segmento | Reserva online 24/7 | Recordatorios automáticos | Fuente y fecha de consulta |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | **DentalSoft** · DentalSoft | Argentina · Clínicas y consultorios dentales | Comprobado: flujo de 4 pasos desde la web de la clínica; solo en plan Pro | Comprobado: WhatsApp y e-mail automáticos en plan Pro (Meta cobra 0,026 USD por mensaje de WhatsApp); en plan Gestión el envío por WhatsApp es manual | https://www.dentalsoft.com.ar/ · 2026-10-15 |
| 2 | **ClinIA (OdontoClinIA)** · Emprinet | Argentina · Consultorios, clínicas PyME y servicios de salud públicos | Comprobado: turnero web y app para pacientes; reserva por WhatsApp con asistente de IA | Comprobado: automáticos por WhatsApp y correo; confirmación, cancelación y reprogramación por el mismo canal | https://www.clinia.com.ar/odontologia · 2026-10-15 |
| 3 | **AgendaPro** · AgendaPro Inc. | Chile / Latam, con sitio para Argentina · Dental, salud y belleza (generalista) | Comprobado: reserva sin registro del paciente y enlace compartible | Comprobado: WhatsApp, SMS o e-mail; doble confirmación | https://agendapro.com/ar/dental/software-odontologico · 2026-10-15 |
| 4 | **DentalCore** · DentalCore | Argentina y Latam (declarado); origen del proveedor no evidenciado · Clínicas dentales | Declarado: "turnos online" en el extracto, sin detalle | Declarado: recordatorios por WhatsApp con confirmación automática | https://dentalcore.app/ · 2026-10-15 (extracto de búsqueda, página no abierta) |
| 5 | **Dentia** · Dentia | Argentina (declarado "hecho en Argentina") · Clínicas odontológicas | Declarado: un asistente de IA agenda por WhatsApp; enlace web de reserva no evidenciado | Declarado: por WhatsApp o e-mail según plan, con confirmación en la agenda | https://dentia.tech/ · 2026-10-15 (extracto de búsqueda, página no abierta) |
| 6 | **DentalTec** · DentalTec | Argentina · Odontólogos, círculos e instituciones | No evidenciado | Declarado: WhatsApp con confirmación del paciente; los packs de mensajes se cobran aparte | https://web.dentaltec.com.ar/preguntas-frecuentes · 2026-10-15 (extracto de búsqueda, página no abierta) |
| 7 | **Turnito** · Turnito | País del proveedor no evidenciado; contenido orientado a Argentina · Negocios con turnos, incluye odontólogos (sin odontograma) | Declarado: agendamiento online 24/7 | Declarado: WhatsApp y e-mail | https://turnito.app/blog/las-mejores-apps-de-turnos-para-odontologos-en-argentina-2026/ · 2026-10-15 (blog del propio proveedor) |
| 8 | **Pedí Tu Turno** · No evidenciado | Argentina · Negocios y consultorios (no específico dental) | Declarado: página pública de reservas | Declarado: confirmación por WhatsApp | https://www.capterra.es/software/1113334/Pedi-Tu-Turno · 2026-10-15 (marketplace de terceros) |
| 9 | **Dentalink** · Engenis SpA (Healthatom) | Chile / Latam; contactos en Chile, Colombia, México y España, ninguno de Argentina · Consultorios y clínicas dentales | Declarado: "Agendamiento online" figura como módulo en la home, sin detalle | Declarado: "Confirmación de citas" y "Tareas automáticas de citas"; canal no especificado | https://www.softwaredentalink.com/ · 2026-10-15 |
| 10 | **Nubimed** · Nubimed | España · Clínicas y centros médicos, con módulo dental | Comprobado: los pacientes piden cita las 24 h eligiendo entre los huecos disponibles | Comprobado: recordatorios diarios automáticos con confirmación o cancelación del paciente; el canal no se detalla en la home (la integración con WhatsApp se lista aparte) | https://www.nubimed.com/ · 2026-10-15 |
| 11 | **Dentidesk** · Dentidesk | Chile / Latam · Clínicas dentales | Parcial: el agendamiento online es un add-on en Integraciones | No evidenciado: el WhatsApp automático figura como "una de las próximas alternativas" (nota publicada el 2026-08-13) | https://www.dentidesk.com/ · 2026-10-15 |
| 12 | **Nimbo** · Ecaresoft Inc. | México / Latam, con sitios para AR, EC y PE · Clínicas y consultorios (vertical dental) | Parcial: el portal del paciente da acceso a citas; la reserva autónoma no es explícita | Comprobado: módulo de recordatorios automatizados; canal no detallado en la home | https://www.nimbo-x.com/ · 2026-10-15 |
| 13 | **Doctoralia** · No evidenciado | España / Argentina · Médicos y odontólogos | No evidenciado | No evidenciado | https://www.doctoralia.com.ar/ · no consultada: el sitio bloquea la lectura automatizada |
| 14 | **Medesk** · Medesk | Internacional, más de 50 países (declarado) · Clínicas dentales y consultas privadas | No evidenciado | Declarado: mensajes y recordatorios automáticos | https://www.medesk.net/es/solutiones/odontologia · 2026-10-15 (extracto de búsqueda, página no abierta) |
| 15 | **DentalSoft Plus** · No evidenciado | No evidenciado · Clínicas y consultorios dentales | No evidenciado | Declarado por un tercero: WhatsApp, SMS y e-mail | https://www.comparasoftware.com/dentasoftplus · 2026-10-15 (comparador de terceros) |

**Notas.** Los sitios de Sintec Odonto, TurnosWeb, OdontoSys, XDental, Medisystem, Geodonto, SoftDental y ConsultorioMovil, que figuraban en una versión anterior de esta tabla, se retiraron: no se pudo abrir ni corroborar su existencia o sus funciones. La fila 15 se mantiene solo para llegar a la muestra mínima y es la de menor respaldo; conviene reemplazarla si aparece un sistema con sitio oficial verificable.

\newpage

## B. Matriz de puntuación (0 a 5)

### B.1 Nota metodológica

**Alcance.** Se puntúan los siete sistemas cuyo sitio oficial se leyó completo el 2026-10-15: DentalSoft, ClinIA, AgendaPro, Nubimed, Dentalink, Dentidesk y Nimbo. Los ocho restantes de la tabla A **no se puntúan** porque la evidencia es un extracto, un tercero o no existe; puntuarlos sería inventar precisión.

**Escala.**

| Puntaje | Significado |
| :-: | :--- |
| 5 | Funcionalidad completa y documentada en el sitio oficial, aplicable a Argentina |
| 4 | Completa con una limitación menor (canal no especificado, plan superior, un componente local ausente) |
| 3 | Cobertura parcial, genérica o pensada para otro mercado |
| 2 | Funcionalidad básica o anunciada pero aún no disponible |
| 1 | Mencionada sin detalle verificable |
| 0 | Ausente |
| NE | No evidenciado en las fuentes consultadas. **No cuenta como 0** |

**Reglas.**

1. Se puntúa solo lo que el sitio oficial describe. No se probaron los sistemas y los puntajes son juicios del analista sobre información comercial.
2. Si una función depende del plan, se puntúa el plan más completo descripto públicamente; la dependencia se refleja en "Precio y facilidad de adopción".
3. Una función anunciada como "próxima" puntúa 2 como máximo.
4. **Tratamiento de NE:** el total ponderado se calcula solo sobre los criterios evidenciados, reescalando sus pesos a 100 %. Cada sistema muestra su **cobertura**; con cobertura menor a 100 % el puntaje es menos firme.
5. El contexto de referencia es un consultorio argentino. "Integraciones locales y WhatsApp" premia WhatsApp, obras sociales, medios de pago locales y fiscalidad ARCA, y penaliza integraciones de otros países. Un 5 requiere WhatsApp, obras sociales y fiscalidad argentina.
6. Diferencias menores a 0,2 puntos no deben leerse como una ventaja real.

### B.2 Matriz

| Criterio | Peso | DentalSoft | ClinIA | Nubimed | AgendaPro | Dentalink | Dentidesk | Nimbo |
| :--- | -: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Gestión de turnos y automatización | 25 % | 5 | 5 | 5 | 5 | 4 | 2 | 3 |
| Funcionalidad odontológica clínica | 20 % | 5 | 4 | 4 | 4 | 5 | 5 | 3 |
| Integraciones locales y WhatsApp | 15 % | 4 | 5 | 3 | 3 | 2 | 2 | 2 |
| Administración, cobros y facturación | 15 % | 4 | 5 | 4 | 4 | 4 | 4 | 3 |
| Experiencia del paciente | 10 % | 5 | 4 | 5 | 4 | 4 | 3 | 4 |
| Seguridad, exportación y trazabilidad | 10 % | 3 | 3 | 3 | NE | 4 | NE | NE |
| Precio y facilidad de adopción | 5 % | 5 | 3 | 4 | 3 | 3 | 3 | NE |
| **Total de pesos** | **100 %** | | | | | | | |
| **Cobertura** | | 100 % | 100 % | 100 % | 90 % | 100 % | 90 % | 85 % |
| **Puntuación ponderada (sobre 5)** | | **4,50** | **4,40** | **4,10** | **4,06** | **3,85** | **3,17** | **2,94** |
| **Posición** | | 1 | 2 | 3 | 4 | 5 | 6 | 7 |

DentalSoft y ClinIA están prácticamente empatados (0,10 de diferencia), y Nubimed y AgendaPro también (0,04). AgendaPro, Dentidesk y Nimbo tienen cobertura menor a 100 %.

### B.3 Justificación por sistema

**DentalSoft (4,50).** *Turnos 5:* turnos online 24/7, recordatorios automáticos por WhatsApp y e-mail que actualizan la agenda, sincronización con Google Calendar y recepcionista virtual; los automáticos requieren el plan Pro. *Clínica 5:* odontograma con 18 estados, ortodoncia, historia clínica, consentimientos con firma y recetas digitales. *Integraciones 4:* WhatsApp, Google Calendar, MercadoPago y más de 20 obras sociales; no menciona ARCA. *Administración 4:* caja, cobros, liquidaciones de profesionales y de obras sociales, presupuestos y reportes; no menciona facturación electrónica. *Paciente 5:* reserva en 4 pasos, portal del paciente, confirmación por WhatsApp. *Seguridad 3:* permisos por rol e historial de cambios con profesional y fecha, exportación a PDF y Excel; sin certificaciones declaradas. *Precio 5:* precios públicos por profesional, tres meses de prueba y migración incluida; los mensajes de WhatsApp tienen costo aparte.

**ClinIA (4,40).** *Turnos 5:* turnero web y app, reserva por WhatsApp con asistente de IA validada contra la agenda real, recordatorios, cancelación y reprogramación, agenda por profesional, especialidad o sillón. *Clínica 4:* odontograma FDI de 52 piezas versionado, plan de tratamiento, historia clínica con CIE-10 y recetario registrado en ReNaPDiS; no menciona periodontograma ni ortodoncia. *Integraciones 5:* WhatsApp, ARCA, API de PUCO, RENAPER y módulos para PAMI y SUMAR+. *Administración 5:* facturación electrónica ARCA, obras sociales y prepagas, caja con arqueo en pesos, dólares o euros. *Paciente 4:* app y turnero web; no menciona portal con historial. *Seguridad 3:* copias de seguridad cada 10 minutos, odontograma bloqueado al finalizar cada versión, acceso controlado; existe una página de seguridad que no se leyó. *Precio 3:* cotización por institución sin costo por usuario ni de migración; sin precios publicados.

**Nubimed (4,10).** *Turnos 5:* citas 24 h, recordatorios diarios automáticos con confirmación o cancelación, lista y sala de espera, videollamada. *Clínica 4:* módulo dental con odontograma y periodontograma, historia clínica personalizable; producto generalista. *Integraciones 3:* integración con WhatsApp; el marco fiscal y de mutuas es español (Verifactu, TicketBAI). *Administración 4:* contabilidad, facturación, remesas, mutuas y liquidación a profesionales. *Paciente 5:* portal del paciente, reserva 24 h, pago online anticipado, videoconsulta, firma digital. *Seguridad 3:* acceso cifrado, copias de seguridad y firma biométrica; sin certificaciones leídas. *Precio 4:* pago mensual por uso, sin permanencia, traspaso gratuito de datos.

**AgendaPro (4,06, cobertura 90 %).** *Turnos 5:* reserva sin registro, enlace compartible, recordatorios por WhatsApp, SMS o e-mail con doble confirmación, liberación automática de espacios; indica que sirve a consultorios con uno o varios sillones. *Clínica 4:* historia clínica odontológica editable, registro de tratamientos y evolución, imágenes adjuntas y presupuestos digitales; el odontograma digital se nombra solo en la descripción de la página. *Integraciones 3:* WhatsApp y pagos integrados a la agenda; no nombra ARCA, obras sociales ni MercadoPago. *Administración 4:* caja en tiempo real, señas, comisiones, reportes de facturación por profesional y sede, inventario; no menciona facturación electrónica. *Paciente 4:* reserva sin registro, seña al reservar, marketplace gratuito. *Seguridad NE:* sin información en la página leída. *Precio 3:* prueba gratuita; existe una página de precios que no se leyó.

**Dentalink (3,85).** *Turnos 4:* agendamiento online, confirmación y tareas automáticas de citas, campañas por e-mail; sin detalle de canal. *Clínica 5:* historia clínica, odontograma y periodontograma, módulo de ortodoncia (plan Titanium), consentimientos, firma electrónica. *Integraciones 2:* sin WhatsApp ni integraciones argentinas evidenciadas; ofrece seguros, financiamiento y pagos a escala Latam. *Administración 4:* cajas, pagos online, cobro en cuotas, cálculo de pago a odontólogos, inventario y laboratorios; sin facturación electrónica. *Paciente 4:* reserva online, encuestas NPS, firma electrónica, videoconsulta. *Seguridad 4:* declara ISO 27001, HIPAA y GDPR, respaldos diarios y tráfico cifrado (declarado, no auditado). *Precio 3:* planes Esencial, Pro y Titanium por cotización, migración acompañada.

**Dentidesk (3,17, cobertura 90 %).** *Turnos 2:* agenda avanzada; la reserva online es un add-on y el WhatsApp automático es futuro. *Clínica 5:* fichas de odontograma, endodoncia, periodoncia, ortodoncia y cirugía ortognática, interconsultas y multisucursal. *Integraciones 2:* SII de Chile y Alegra (República Dominicana); nada para Argentina. *Administración 4:* facturación propia integrada con el SII, más de 20 reportes y control de stock; marco fiscal de Chile. *Paciente 3:* app móvil y firma de consentimientos. *Seguridad NE.* *Precio 3:* prueba de 15 días y migración asistida; sin precios.

**Nimbo (2,94, cobertura 85 %).** *Turnos 3:* agenda y recordatorios automatizados, telemedicina; la reserva autónoma no es explícita. *Clínica 3:* vertical dental con odontograma online dentro de un producto generalista; el enlace "Ver más" de esa sección está roto en la home. *Integraciones 2:* encuestas por WhatsApp; el marco declarado es mexicano (NOM, COFEPRIS). *Administración 3:* facturación electrónica con validez oficial (México), inventarios y reportes. *Paciente 4:* portal del paciente, encuestas y telemedicina. *Seguridad NE y Precio NE:* hay páginas para ambos criterios que no se leyeron.

\newpage

## C. Análisis competitivo

### C.1 Funcionalidades que ya son estándar de mercado

Entre los siete sistemas puntuados:

- **Agenda multiprofesional en la nube**, con migración asistida desde el sistema anterior y prueba o demo gratuita (DentalSoft, ClinIA, Dentalink, Dentidesk, Nubimed, AgendaPro).
- **Recordatorios automáticos**: seis de los siete los describen. Dentidesk es la excepción, ya que su WhatsApp automático aún no está disponible.
- **Reserva online del paciente**: la ofrecen o la declaran DentalSoft, ClinIA, AgendaPro, Nubimed y Dentalink; en Dentidesk es un add-on.
- **Historia clínica digital y odontograma** en los productos específicamente odontológicos (DentalSoft, ClinIA, Dentalink, Dentidesk) y en el módulo dental de Nubimed.

Una agenda online con recordatorios, sola, no constituye una diferencia.

### C.2 Funcionalidades diferenciadoras reales

Solo se listan funciones descriptas en el sitio oficial; el resto es afirmación comercial.

- **ClinIA:** asistente de IA que agenda, recuerda, cancela y reprograma por WhatsApp contra la agenda real; facturación ARCA; verificación de cobertura con PUCO; recetario registrado en ReNaPDiS (el registro público se puede consultar); agenda por sillón.
- **DentalSoft:** liquidaciones de obras sociales y de profesionales, página web de la clínica con turnos integrados, recepcionista virtual 24 h y **precios públicos**.
- **Dentalink:** certificaciones de seguridad declaradas, financiamiento y seguros para pacientes, módulos de IA para radiografías.
- **AgendaPro:** reserva sin registro, cobro de seña al reservar y marketplace gratuito.
- **Dentidesk:** fichas clínicas especializadas y gestión multisucursal.

### C.3 Vacíos frecuentes del mercado argentino

Son **hipótesis** derivadas de lo que *no* se evidenció; no equivalen a necesidades confirmadas.

1. **WhatsApp automático ligado al plan alto y con costo aparte.** En DentalSoft solo está en el plan Pro, el plan base envía manualmente, y Meta cobra por mensaje.
2. **Precios no publicados.** Dentalink, Dentidesk y ClinIA trabajan por cotización; solo DentalSoft publica importes entre los sistemas leídos.
3. **Gestión explícita de sillones.** ClinIA y AgendaPro los mencionan; no se documenta en las páginas leídas de DentalSoft, Dentalink ni Nubimed.
4. **Facturación electrónica ARCA.** Solo ClinIA la nombra entre los sistemas leídos; DentalSoft y AgendaPro no la mencionan.
5. **Privacidad de datos de salud.** Ninguna fuente leída declara explícitamente adecuación a la normativa argentina de datos personales; Dentalink declara certificaciones internacionales.
6. **Productos de origen extranjero.** Dentalink, Dentidesk, Nubimed y Nimbo orientan su fiscalidad y sus integraciones a Chile, España o México.

### C.4 Oportunidades de innovación

1. **Agenda que impide la doble reserva de profesional y sillón de forma atómica**, con errores explícitos que no exponen datos de otros pacientes. Es la base del change implementado en este proyecto.
2. **Recordatorios por WhatsApp accesibles desde el plan base**, con consentimiento registrado, estado de entrega y fallos visibles.
3. **Precio y alcance transparentes** para consultorios pequeños, frente a modelos de cotización.
4. **Datos mínimos por diseño:** operar la agenda sin recopilar datos clínicos reduce la superficie de datos sensibles.
5. **Simplicidad de adopción** para consultorios con agenda en papel o dispersa.

**Amenazas.** DentalSoft y ClinIA ya combinan agenda, WhatsApp y obras sociales con evidencia pública. Agregar funciones clínicas, fiscales o de obras sociales antes de validar la demanda aumentaría costos y superficie de datos.

\newpage

## D. Recomendación final

### D.1 Cinco competidores prioritarios para analizar mediante demo

| # | Competidor | Por qué |
|:-:|:--|:--|
| 1 | **DentalSoft** | Líder de la matriz (4,50) y benchmark local de adopción, precio y flujos argentinos. |
| 2 | **ClinIA** | Casi empatado en el primer lugar (4,40); es el único con ARCA, PUCO y asistente de WhatsApp con IA, y agenda por sillón. |
| 3 | **AgendaPro** | Referente de agenda y administración, con reserva sin registro y menciona sillones. |
| 4 | **Dentalink** | Referente de suite clínica especializada y de seguridad declarada. |
| 5 | **Dentia** | Competidor argentino reciente centrado en un asistente de WhatsApp que agenda; su evidencia es solo un extracto y debe verificarse en la demo. |

**Condiciones de la demo.** Se usan demostraciones públicas, videos oficiales o paneles de prueba con **datos ficticios**. No se contactan proveedores ni se cargan datos personales reales.

### D.2 Tres productos de referencia de experiencia de usuario

1. **DentalSoft:** reserva del paciente en cuatro pasos y recordatorio de WhatsApp al que se responde con "1" o "2".
2. **Nubimed:** portal del paciente, sala de espera y lista de espera integradas a la agenda.
3. **AgendaPro:** reserva sin que el paciente deba registrarse y enlace compartible por redes.

### D.3 MVP sugerido

**Imprescindible (P0)**

- Configuración de consultorio, zona horaria, profesionales, servicios, horarios y roles básicos.
- Pacientes con datos mínimos de contacto, sin datos clínicos.
- Agenda por profesional; crear, confirmar, reprogramar y cancelar turnos; estados operativos.
- Prevención atómica de solapamientos por profesional y, si el consultorio los administra, por sillón; los turnos consecutivos están permitidos.
- Registro de actor y fecha, y permisos por rol.

**Diferenciador (a validar)**

- Error de conflicto explícito, con el recurso afectado y sin datos del otro paciente.
- Confirmaciones y recordatorios por WhatsApp con consentimiento, estado de entrega y fallos visibles. **Puerta de decisión:** proveedor, costo por mensaje y consentimiento deben validarse antes del piloto.
- Plan y precio transparentes.

**Etapas posteriores**

- Odontograma e historia clínica, ortodoncia y recetas.
- Facturación electrónica ARCA, obras sociales y liquidaciones.
- Pagos y MercadoPago, portal de autogestión del paciente, videoconsulta.
- Chatbot o asistente con IA, campañas, inventario, integración con Google Calendar, multisucursal y reportes avanzados.

### D.4 Supuestos y próximos pasos

- El cliente objetivo (uno a cinco profesionales), el dolor de coordinación y la relevancia del sillón son **hipótesis**; hay que entrevistar consultorios.
- Decidir con usuarios si un odontograma básico es condición para el piloto.
- Validar proveedor, costo y consentimiento de WhatsApp.
- Los puntajes son juicios documentales; verificar planes, precios y funciones con demos antes de decidir.
- El informe tiene 15 sistemas, pero solo 7 con evidencia suficiente para puntuar. Conviene ampliar la verificación de DentalCore, Dentia y DentalTec.

\newpage

## Verificación de fuentes

| # | Fuente (tipo) | URL | Qué afirmaba el informe | Qué se encontró en la URL | Corrección aplicada | Verificado por el equipo |
|:-:|:--|:--|:--|:--|:--|:--|
| 1 | Dentalink, sitio oficial (home) | https://www.softwaredentalink.com/ | Reserva online "Comprobado"; recordatorios por WhatsApp. | La home solo lista nombres de módulos (agendamiento online, confirmación de citas). No menciona WhatsApp. Declara ISO 27001, HIPAA y GDPR. No hay contacto en Argentina. | Reserva y recordatorios pasan a **Declarado**; se quita WhatsApp. | Yoselie Aquino - 15/10/2026 - Verificado |
| 2 | AgendaPro, página dental de Argentina (oferta comercial) | https://agendapro.com/ar/dental/software-odontologico | "Facturación electrónica según el país"; reserva 24/7. | Confirma reserva sin registro y enlace compartible; recordatorios por WhatsApp, SMS o e-mail; historia clínica, señas, comisiones, inventario y "uno o varios sillones". Habla de "reportes de facturación", **no** de facturación electrónica. El odontograma aparece solo en la descripción de la página. | Se quita la facturación electrónica; Administración 5→4, Integraciones 4→3. | Yoselie Aquino - 15/10/2026 - Verificado |
| 3 | DentalSoft, sitio oficial (página de precios y funciones) | https://www.dentalsoft.com.ar/ | WhatsApp y e-mail automáticos; integraciones 5. | Confirma los recordatorios, pero **solo en el plan Pro**; el plan Gestión los envía a mano. Meta cobra 0,026 USD por mensaje de WhatsApp. No menciona ARCA ni facturación electrónica. Precios públicos: Gestión $30.000/mes, Pro $60.000/mes por profesional. | Se aclara la restricción de plan y el costo; Integraciones 5→4. | Yoselie Aquino - 15/10/2026 - Verificado |
| 4 | Dentidesk, publicación sobre novedades e integraciones | https://www.dentidesk.com/ | Recordatorios "Parcial"; seguridad no evidenciada. | Confirma que la reserva online es un add-on y que el WhatsApp automático es una "próxima alternativa" (nota del 2026-08-13). Facturación integrada con el SII de Chile y Alegra (República Dominicana). Sin información de seguridad. | Recordatorios pasan a **No evidenciado**; Seguridad queda NE. | Yoselie Aquino - 15/10/2026 - Verificado |
| 5 | ClinIA, sitio oficial del módulo odontológico | https://www.clinia.com.ar/odontologia | *(sistema nuevo)* | Confirma turnos con IA por WhatsApp, agenda por sillón, ARCA, PUCO y recetario con número 248 en ReNaPDiS. Aclara que ese registro no implica aprobación general del software. Precios por cotización. | Se incorpora a las tablas A y B. | Yoselie Aquino - 15/10/2026 - Verificado |
| 6 | Nubimed, sitio oficial (home) | https://www.nubimed.com/ | Recordatorios "Comprobado" por canal. | Confirma citas 24 h y recordatorios diarios con confirmación o cancelación; el canal no se detalla (la integración con WhatsApp es una página aparte). Marco fiscal español. | Se aclara que el canal no está especificado. | Yoselie Aquino - 15/10/2026 - Verificado |
| 7 | Nimbo, sitio oficial (home) | https://www.nimbo-x.com/ | Seguridad 3; precio no leído. | Confirma recordatorios, facturación con validez oficial en México y cumplimiento NOM. La sección "Dental" tiene un enlace roto. No se leyeron las páginas de seguridad ni de precios. | Seguridad y Precio pasan a **NE**. | Yoselie Aquino - 15/10/2026 - Verificado |

**Hallazgos más relevantes de la revisión:**

1. La tabla anterior marcaba "Comprobado" funciones que la URL citada no respaldaba (WhatsApp en Dentalink, facturación electrónica en AgendaPro). Se corrigieron.
2. Hay funciones que existen, pero con condiciones que cambian la comparación: los recordatorios automáticos de DentalSoft solo están en el plan Pro y tienen costo por mensaje.
3. Ocho sistemas de una versión anterior de la tabla no pudieron corroborarse y se retiraron.
4. Quedan fuentes sin abrir por el equipo: DentalCore, Dentia, DentalTec, Turnito, Medesk, Pedí Tu Turno, DentalSoft Plus y Doctoralia, marcadas como extracto, tercero o no consultadas.

## Referencias

Fecha de consulta de todas las fuentes: 2026-10-15.

- DentalSoft. https://www.dentalsoft.com.ar/
- ClinIA, módulo odontológico. https://www.clinia.com.ar/odontologia
- AgendaPro Argentina, software odontológico. https://agendapro.com/ar/dental/software-odontologico
- DentalCore. https://dentalcore.app/
- Dentia. https://dentia.tech/
- DentalTec, preguntas frecuentes. https://web.dentaltec.com.ar/preguntas-frecuentes
- Turnito, blog. https://turnito.app/blog/las-mejores-apps-de-turnos-para-odontologos-en-argentina-2026/
- Pedí Tu Turno, ficha en Capterra. https://www.capterra.es/software/1113334/Pedi-Tu-Turno
- Dentalink. https://www.softwaredentalink.com/
- Nubimed. https://www.nubimed.com/
- Dentidesk. https://www.dentidesk.com/
- Nimbo. https://www.nimbo-x.com/
- Doctoralia Argentina. https://www.doctoralia.com.ar/ *(no consultada)*
- Medesk, soluciones para odontología. https://www.medesk.net/es/solutiones/odontologia
- Comparasoftware, DentalSoft Plus. https://www.comparasoftware.com/dentasoftplus
- Registro Nacional de Plataformas Digitales Sanitarias (ReNaPDiS), plataformas de receta electrónica. https://www.argentina.gob.ar/salud/digital/renapdis/receta-electronica/plataformas
