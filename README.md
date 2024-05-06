# Entrega Proyecto 3
Video en youtube: [https://youtu.be/yds9bxsD4N0](https://youtu.be/yds9bxsD4N0)
## Guía para desplegar 
1. **Clonar el repositorio en la carpeta desde la que se quiere ejecutar el notebook**
   ```console
   git clone https://github.com/danielj4mv/proyecto_3.git
   ```
2. **Ingresar desde la terminal a la carpeta en que se encuentra el archivo `docker-compose.yml`**
   ```docker
   cd proyecto_3
   ```
3. **Crear carpetas necesarias para los volúmenes**
   ```console
   mkdir ./airflow/logs
   mkdir ./airflow/plugins
   mkdir ./data/output_data
   ```
4. **Crear la siguiente variable de entorno para poder modificar volúmenes**
   ```console
   echo -e "AIRFLOW_UID=$(id -u)" >> .env
   ```
5. **Crear y ejecutar los servicios establecidos en el `docker-compose.yml`**

   ```docker
   docker compose up airflow-init -d
   docker compose up -d
   ```
   Este proceso puede tomar varios minutos, espere a que termine de ejecutar para pasar al siguiente paso

6. **Una vez se ha terminado de ejecutar el comando anterior, puede proceder a interactuar con los servicios del docker-compose a través de sus apis:**

   - **Airflow:** puerto 8080, las credenciales de acceso están definidas en el `.env`
   - **MLflow:** puerto 8081
   - **Minio:** puerto 8089, las credenciales de acceso están definidas en el `.env`

   Recuerde que si el ingreso es dessde la máquina virtual debe ir a `IP_de_la_MV:Puerto`, desde el pc local sería `Localhost:Puerto`

7. **Para el componente de inferencia, en un cluster en minikube se despliegan dos servicios, uno con un app de fastapi con el cual a partir de una petición en un JSON con los predictores entrega la predicción y otro con una interfaz de streamlit para hacer peticiones facilmente a fastapi, para poner en ejecución estos servicios, lo primero que debe hacer es entrar a la carpeta kubernetes e iniciar minikube**

   ```docker
   cd kubernetes
   minikube start
   ```
8. **El siguiente paso es activar los archivos de configuración de ambos servicios que se encuentran dentro de esta carpeta**

   ```docker
   kubectl apply -f .
   ```
9. **Por último, se expone los puertos de ambos servicios con port-forward**

   ```docker
   kubectl port-forward --address 0.0.0.0 service/fastapi-service 8085:8085 &
   kubectl port-forward --address 0.0.0.0 service/streamlit-service 8087:8087 &
   ```
   Despues de ejecutar estos comandos, puede acceder a el app de fastapi en el puerto 8085 y a la interfaz de streamlit en el puerto 8087 de la ip del localhost (o de la ip de la máquina virtual)
