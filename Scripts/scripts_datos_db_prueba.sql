INSERT INTO public.auth_group (name) VALUES
	 ('Secretaria Recursos Humanos'),
	 ('Director Recursos Humanos'),
	 ('Vicerrector'),
	 ('Director de Programa'),
	 ('Rector');
INSERT INTO public.auth_group_permissions (group_id,permission_id) VALUES
	 (1,9),
	 (1,10),
	 (1,11),
	 (1,12),
	 (2,12);
INSERT INTO public.auth_permission (name,content_type_id,codename) VALUES
	 ('Can add Rol',1,'add_rol'),
	 ('Can change Rol',1,'change_rol'),
	 ('Can delete Rol',1,'delete_rol'),
	 ('Can view Rol',1,'view_rol'),
	 ('Can add Tipo de Documento',2,'add_tipodocumento'),
	 ('Can change Tipo de Documento',2,'change_tipodocumento'),
	 ('Can delete Tipo de Documento',2,'delete_tipodocumento'),
	 ('Can view Tipo de Documento',2,'view_tipodocumento'),
	 ('Can add Usuario',3,'add_usuario'),
	 ('Can change Usuario',3,'change_usuario');
INSERT INTO public.auth_permission (name,content_type_id,codename) VALUES
	 ('Can delete Usuario',3,'delete_usuario'),
	 ('Can view Usuario',3,'view_usuario'),
	 ('Can add log entry',4,'add_logentry'),
	 ('Can change log entry',4,'change_logentry'),
	 ('Can delete log entry',4,'delete_logentry'),
	 ('Can view log entry',4,'view_logentry'),
	 ('Can add permission',5,'add_permission'),
	 ('Can change permission',5,'change_permission'),
	 ('Can delete permission',5,'delete_permission'),
	 ('Can view permission',5,'view_permission');
INSERT INTO public.auth_permission (name,content_type_id,codename) VALUES
	 ('Can add group',6,'add_group'),
	 ('Can change group',6,'change_group'),
	 ('Can delete group',6,'delete_group'),
	 ('Can view group',6,'view_group'),
	 ('Can add user',7,'add_user'),
	 ('Can change user',7,'change_user'),
	 ('Can delete user',7,'delete_user'),
	 ('Can view user',7,'view_user'),
	 ('Can add content type',8,'add_contenttype'),
	 ('Can change content type',8,'change_contenttype');
INSERT INTO public.auth_permission (name,content_type_id,codename) VALUES
	 ('Can delete content type',8,'delete_contenttype'),
	 ('Can view content type',8,'view_contenttype'),
	 ('Can add session',9,'add_session'),
	 ('Can change session',9,'change_session'),
	 ('Can delete session',9,'delete_session'),
	 ('Can view session',9,'view_session');
INSERT INTO public.auth_user ("password",last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) VALUES
	 ('pbkdf2_sha256$870000$2XaKq2SVgq4bGixe5eJh7O$as4gb0HwVGzQb48lp9cd4K89jUR+XL9Lt4RdkhJltjY=',NULL,false,'secretaria.thumano@unicorsalud.edu.co','','','',false,true,'2024-12-02 15:36:55-05'),
	 ('pbkdf2_sha256$870000$U91iMIxKXUKRVTZ1RRwKF9$cGaJfgDCGXuppfpybI4PtH3FHdNvfp1WaMK/QaQ0e4w=','2024-12-03 21:28:23.210149-05',true,'admin','','','admin@unicorsalud.edu.co',true,true,'2024-12-02 15:25:26.024614-05');
INSERT INTO public.auth_user_groups (user_id,group_id) VALUES
	 (2,1);
INSERT INTO public.django_admin_log (action_time,object_id,object_repr,action_flag,change_message,content_type_id,user_id) VALUES
	 ('2024-12-02 15:31:50.543173-05','1','AD - Administrativo y Docente',1,'[{"added": {}}]',1,1),
	 ('2024-12-02 15:32:10.308847-05','2','A - Administrativo',1,'[{"added": {}}]',1,1),
	 ('2024-12-02 15:32:20.046802-05','3','D - Docente',1,'[{"added": {}}]',1,1),
	 ('2024-12-02 15:36:56.144278-05','2','secretaria.thumano@unicorsalud.edu.co',1,'[{"added": {}}]',7,1),
	 ('2024-12-02 15:43:29.253866-05','1','CC - Cédula de Ciudadanía',1,'[{"added": {}}]',2,1),
	 ('2024-12-02 15:43:42.203605-05','2','CE - Cédula de Extranjería',1,'[{"added": {}}]',2,1),
	 ('2024-12-02 15:44:01.084056-05','3','TI - Tarjeta de Identidad',1,'[{"added": {}}]',2,1),
	 ('2024-12-02 15:44:34.020086-05','4','PEP - Permiso Especial de Permanencia',1,'[{"added": {}}]',2,1),
	 ('2024-12-02 15:45:07.502104-05','5','PA - Permiso de Permanencia',1,'[{"added": {}}]',2,1),
	 ('2024-12-02 15:45:32.586889-05','6','RC - Registro Civil',1,'[{"added": {}}]',2,1);
INSERT INTO public.django_admin_log (action_time,object_id,object_repr,action_flag,change_message,content_type_id,user_id) VALUES
	 ('2024-12-02 15:54:13.488275-05','1','LISBETH HERNANDEZ',1,'[{"added": {}}]',3,1),
	 ('2024-12-02 16:22:09.155775-05','1','Secretaria Recursos Humanos',1,'[{"added": {}}]',6,1),
	 ('2024-12-02 16:23:31.337064-05','2','secretaria.thumano@unicorsalud.edu.co',2,'[{"changed": {"fields": ["Groups"]}}]',7,1),
	 ('2024-12-02 16:24:26.468104-05','2','Director Recursos Humanos',1,'[{"added": {}}]',6,1),
	 ('2024-12-02 16:24:58.591055-05','2','Director Recursos Humanos',2,'[{"changed": {"fields": ["Permissions"]}}]',6,1),
	 ('2024-12-02 16:25:58.189472-05','3','Directores de Programas',1,'[{"added": {}}]',6,1),
	 ('2024-12-02 16:45:27.836725-05','4','Vicerrector',1,'[{"added": {}}]',6,1),
	 ('2024-12-02 16:45:51.570463-05','3','Director de Programa',2,'[{"changed": {"fields": ["Name"]}}]',6,1),
	 ('2024-12-02 16:46:29.667982-05','5','Rector',1,'[{"added": {}}]',6,1),
	 ('2024-12-03 21:29:53.840251-05','6','RC - Registro Civil',2,'[]',2,1);
INSERT INTO public.django_admin_log (action_time,object_id,object_repr,action_flag,change_message,content_type_id,user_id) VALUES
	 ('2024-12-03 21:30:51.652743-05','5','TI - Tarjeta de Identidad',2,'[{"changed": {"fields": ["Tipo documento", "Descripcion"]}}]',2,1),
	 ('2024-12-03 21:31:18.52243-05','4','CC - Cédula de Ciudadanía',2,'[{"changed": {"fields": ["Tipo documento", "Descripcion"]}}]',2,1),
	 ('2024-12-03 21:37:15.492642-05','3','PEP - Permiso Especial de Permanencia',2,'[{"changed": {"fields": ["Tipo documento", "Descripcion"]}}]',2,1),
	 ('2024-12-03 21:37:57.059377-05','3','PEP - Cédula de Extranjería',2,'[{"changed": {"fields": ["Descripcion"]}}]',2,1),
	 ('2024-12-03 21:38:15.452721-05','3','CE - Cédula de Extranjería',2,'[{"changed": {"fields": ["Tipo documento"]}}]',2,1),
	 ('2024-12-03 21:38:42.900756-05','2','PP - Pasaporte',2,'[{"changed": {"fields": ["Tipo documento", "Descripcion"]}}]',2,1),
	 ('2024-12-03 21:39:24.306049-05','1','PEP - Permiso Especial de Permanencia',2,'[{"changed": {"fields": ["Tipo documento", "Descripcion"]}}]',2,1),
	 ('2024-12-03 21:57:31.508939-05','7','PPT - PERMISO POR PROTECCION TEMPORAL',1,'[{"added": {}}]',2,1),
	 ('2024-12-03 21:58:14.464038-05','7','PPT - Permiso por Protección Temporal',2,'[{"changed": {"fields": ["Descripcion"]}}]',2,1);
INSERT INTO public.django_content_type (app_label,model) VALUES
	 ('dashboard_talento_humano','rol'),
	 ('dashboard_talento_humano','tipodocumento'),
	 ('dashboard_talento_humano','usuario'),
	 ('admin','logentry'),
	 ('auth','permission'),
	 ('auth','group'),
	 ('auth','user'),
	 ('contenttypes','contenttype'),
	 ('sessions','session');
INSERT INTO public.django_migrations (app,name,applied) VALUES
	 ('contenttypes','0001_initial','2024-12-02 15:24:01.941235-05'),
	 ('auth','0001_initial','2024-12-02 15:24:05.906356-05'),
	 ('admin','0001_initial','2024-12-02 15:24:06.939991-05'),
	 ('admin','0002_logentry_remove_auto_add','2024-12-02 15:24:07.077321-05'),
	 ('admin','0003_logentry_add_action_flag_choices','2024-12-02 15:24:07.472778-05'),
	 ('contenttypes','0002_remove_content_type_name','2024-12-02 15:24:08.266401-05'),
	 ('auth','0002_alter_permission_name_max_length','2024-12-02 15:24:08.785035-05'),
	 ('auth','0003_alter_user_email_max_length','2024-12-02 15:24:09.316899-05'),
	 ('auth','0004_alter_user_username_opts','2024-12-02 15:24:09.578482-05'),
	 ('auth','0005_alter_user_last_login_null','2024-12-02 15:24:10.235461-05');
INSERT INTO public.django_migrations (app,name,applied) VALUES
	 ('auth','0006_require_contenttypes_0002','2024-12-02 15:24:10.499226-05'),
	 ('auth','0007_alter_validators_add_error_messages','2024-12-02 15:24:10.892871-05'),
	 ('auth','0008_alter_user_username_max_length','2024-12-02 15:24:11.544634-05'),
	 ('auth','0009_alter_user_last_name_max_length','2024-12-02 15:24:12.077182-05'),
	 ('auth','0010_alter_group_name_max_length','2024-12-02 15:24:12.593455-05'),
	 ('auth','0011_update_proxy_permissions','2024-12-02 15:24:12.865451-05'),
	 ('auth','0012_alter_user_first_name_max_length','2024-12-02 15:24:13.526162-05'),
	 ('dashboard_talento_humano','0001_initial','2024-12-02 15:24:15.649488-05'),
	 ('sessions','0001_initial','2024-12-02 15:24:16.444694-05');
INSERT INTO public.django_session (session_key,session_data,expire_date) VALUES
	 ('k3z1exhb2paw1zett8c5ft9fn9oguewm','.eJxVjMsOwiAQRf-FtSFQ3i7d-w1kmAGpGkhKuzL-uzbpQrf3nHNfLMK21riNvMSZ2JlJdvrdEuAjtx3QHdqtc-xtXebEd4UfdPBrp_y8HO7fQYVRvzUkrY0t5HywWQeJIEpJxmCYrHJKAjkyUmUEi-AL6Uk49MUJZ7VM1rD3B-xQN94:1tIEPA:Ez15IFNIU9i3RgL9TIXracITH1gd822w4cOzJo8GTZo','2024-12-16 16:56:32.491453-05'),
	 ('tfx3cwqk8qiu4plhc4p0kkese3qn79wy','.eJxVjMsOwiAQRf-FtSFQ3i7d-w1kmAGpGkhKuzL-uzbpQrf3nHNfLMK21riNvMSZ2JlJdvrdEuAjtx3QHdqtc-xtXebEd4UfdPBrp_y8HO7fQYVRvzUkrY0t5HywWQeJIEpJxmCYrHJKAjkyUmUEi-AL6Uk49MUJZ7VM1rD3B-xQN94:1tIGTT:ZV6w9XbhSq6EtAZ7bHGwRdR9TJ6Jhme_4_WZDlo9V6c','2024-12-16 19:09:07.857412-05'),
	 ('9uhy8rib2k928g4g62fkj7k8fuyu911f','.eJxVjMsOwiAQRf-FtSFQ3i7d-w1kmAGpGkhKuzL-uzbpQrf3nHNfLMK21riNvMSZ2JlJdvrdEuAjtx3QHdqtc-xtXebEd4UfdPBrp_y8HO7fQYVRvzUkrY0t5HywWQeJIEpJxmCYrHJKAjkyUmUEi-AL6Uk49MUJZ7VM1rD3B-xQN94:1tIV59:Q53ST0tAEOd6E4qAHUYsILl0SwqCZX9kVKMY0poynMk','2024-12-17 10:44:59.113066-05'),
	 ('u7d9h4p5tjqd2n1hlcq68agwy03140vx','.eJxVjMsOwiAQRf-FtSFQ3i7d-w1kmAGpGkhKuzL-uzbpQrf3nHNfLMK21riNvMSZ2JlJdvrdEuAjtx3QHdqtc-xtXebEd4UfdPBrp_y8HO7fQYVRvzUkrY0t5HywWQeJIEpJxmCYrHJKAjkyUmUEi-AL6Uk49MUJZ7VM1rD3B-xQN94:1tIf7n:XKHnt_941UjeRpW8gBMePYGC4DRZeAJ5p2uXXEldkTM','2024-12-17 21:28:23.380572-05');
INSERT INTO public.roles (rol,descripcion,fecha_creacion,fecha_modificacion) VALUES
	 ('AD','Administrativo y Docente','2024-12-02 15:31:50.276297-05','2024-12-02 15:31:50.276297-05'),
	 ('A','Administrativo','2024-12-02 15:32:10.043097-05','2024-12-02 15:32:10.043097-05'),
	 ('D','Docente','2024-12-02 15:32:19.802464-05','2024-12-02 15:32:19.802464-05');
INSERT INTO public.tipo_documentos (tipo_documento,descripcion,fecha_creacion,fecha_modificacion) VALUES
	 ('PEP','Permiso Especial de Permanencia','2024-12-02 15:45:32.328272-05','2024-12-03 21:29:53.694997-05'),
	 ('PP','Pasaporte','2024-12-02 15:45:07.230365-05','2024-12-03 21:30:51.517024-05'),
	 ('CE','Cédula de Extranjería','2024-12-02 15:44:33.762633-05','2024-12-03 21:31:18.376664-05'),
	 ('CC','Cédula de Ciudadanía','2024-12-02 15:44:00.807021-05','2024-12-03 21:38:15.305415-05'),
	 ('TI','Tarjeta de Identidad','2024-12-02 15:43:41.946132-05','2024-12-03 21:38:42.759961-05'),
	 ('RC','Registro Civil','2024-12-02 15:43:28.985457-05','2024-12-03 21:39:24.146549-05'),
	 ('PPT','Permiso por Protección Temporal','2024-12-03 21:57:31.188372-05','2024-12-03 21:58:14.326915-05');
INSERT INTO public.usuarios (cargo,primer_nombre,segundo_nombre,primer_apellido,segundo_apellido,fecha_nacimiento,lugar_nacimiento,numero_documento,fecha_expedicion_documento,lugar_expedicion_documento,sexo,telefono_fijo,celular,correo_personal,estado_civil,ultimo_nivel_estudio,eps,arl,afp,caja_compensacion,direccion_residencia,departamento_residencia,ciudad_residencia,barrio_residencia,estado_revision,activo,fecha_creacion,fecha_modificacion,auth_user_id,fk_creado_por_id,fk_modificado_por_id,fk_rol_id,fk_tipo_documento_id) VALUES
	 ('ASISTENTE DE TALENTO HUMANO','LISBETH','LUCILA','HERNANDEZ','MORALES','1995-01-18',NULL,1127584776,NULL,NULL,'FEMENINO',NULL,'3002933708','lisbethhernandezm18@gmail.com',NULL,NULL,'EPS SURA','ARL SURA','AFP PORVENIR','CAJA DE COMPENSACIÓN FAMILIAR - COMFAMILIAR','CARRERA 16 # 31 - 220','ATLÁNTICO','BARRANQUILLA',NULL,'ACEPTADO',true,'2024-12-02 15:54:13.353338-05','2024-12-02 15:54:13.353338-05',2,1,1,2,1);
