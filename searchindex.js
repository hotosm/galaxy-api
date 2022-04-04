Search.setIndex({docnames:["API","API.auth","API.changesets","API.countries","API.data","galaxy","galaxy.query_builder","galaxy.validation","index","modules"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["API.rst","API.auth.rst","API.changesets.rst","API.countries.rst","API.data.rst","galaxy.rst","galaxy.query_builder.rst","galaxy.validation.rst","index.rst","modules.rst"],objects:{"":{API:[0,0,0,"-"],galaxy:[5,0,0,"-"]},"API.BaseModel":{Config:[0,1,1,""]},"API.BaseModel.Config":{alias_generator:[0,2,1,""],allow_population_by_field_name:[0,3,1,""]},"API.auth":{AuthUser:[1,1,1,""],Login:[1,1,1,""],Token:[1,1,1,""],login_required:[1,4,1,""],routers:[1,0,0,"-"]},"API.auth.AuthUser":{id:[1,3,1,""],img_url:[1,3,1,""],username:[1,3,1,""]},"API.auth.Login":{url:[1,3,1,""]},"API.auth.Token":{access_token:[1,3,1,""]},"API.auth.routers":{callback:[1,4,1,""],login_url:[1,4,1,""],my_data:[1,4,1,""]},"API.changesets":{ChangesetResult:[2,1,1,""],FilterParams:[2,1,1,""],PolygonFilter:[2,1,1,""],routers:[2,0,0,"-"],utils:[2,0,0,"-"]},"API.changesets.ChangesetResult":{added_highway:[2,3,1,""],added_highway_km:[2,3,1,""],contributors:[2,3,1,""],deleted_highway:[2,3,1,""],deleted_highway_km:[2,3,1,""],modified_highway:[2,3,1,""],modified_highway_km:[2,3,1,""],name:[2,3,1,""],total_changesets:[2,3,1,""]},"API.changesets.FilterParams":{end_datetime:[2,3,1,""],hashtag:[2,3,1,""],matching_types:[2,2,1,""],start_datetime:[2,3,1,""],type:[2,3,1,""],value:[2,3,1,""]},"API.changesets.PolygonFilter":{geojson:[2,3,1,""],iso3:[2,3,1,""]},"API.changesets.routers":{get_changesets:[2,4,1,""]},"API.changesets.utils":{geom_filter_subquery:[2,4,1,""]},"API.countries":{routers:[3,0,0,"-"]},"API.countries.routers":{get_countries:[3,4,1,""]},"API.data":{routers:[4,0,0,"-"]},"API.data.routers":{callback:[4,4,1,""],login_url:[4,4,1,""]},"API.data_quality":{data_quality_hashtag_reports:[0,4,1,""],data_quality_reports:[0,4,1,""]},"API.mapathon":{get_mapathon_detailed_report:[0,4,1,""],get_mapathon_summary:[0,4,1,""]},"API.organization":{get_ogranization_stat:[0,4,1,""]},"API.osm_users":{list_users:[0,4,1,""],user_statistics:[0,4,1,""]},"API.trainings":{get_organisations_list:[0,4,1,""],get_trainings_list:[0,4,1,""]},"galaxy.DataQuality":{get_report:[5,2,1,""],get_report_as_csv:[5,2,1,""]},"galaxy.Database":{close_conn:[5,2,1,""],connect:[5,2,1,""],executequery:[5,2,1,""]},"galaxy.Mapathon":{get_detailed_report:[5,2,1,""],get_summary:[5,2,1,""]},"galaxy.Output":{to_CSV:[5,2,1,""],to_GeoJSON:[5,2,1,""],to_JSON:[5,2,1,""],to_dict:[5,2,1,""],to_list:[5,2,1,""]},"galaxy.app":{DataQuality:[5,1,1,""],DataQualityHashtags:[5,1,1,""],Database:[5,1,1,""],Insight:[5,1,1,""],Mapathon:[5,1,1,""],OrganizationHashtags:[5,1,1,""],Output:[5,1,1,""],TaskingManager:[5,1,1,""],Training:[5,1,1,""],Underpass:[5,1,1,""],UserStats:[5,1,1,""],check_for_json:[5,4,1,""],print_psycopg2_exception:[5,4,1,""]},"galaxy.app.DataQuality":{get_report:[5,2,1,""],get_report_as_csv:[5,2,1,""]},"galaxy.app.DataQualityHashtags":{get_report:[5,2,1,""],to_csv_stream:[5,2,1,""],to_geojson:[5,2,1,""]},"galaxy.app.Database":{close_conn:[5,2,1,""],connect:[5,2,1,""],executequery:[5,2,1,""]},"galaxy.app.Insight":{get_mapathon_detailed_result:[5,2,1,""],get_mapathon_summary_result:[5,2,1,""]},"galaxy.app.Mapathon":{get_detailed_report:[5,2,1,""],get_summary:[5,2,1,""]},"galaxy.app.OrganizationHashtags":{get_report:[5,2,1,""],get_report_as_csv:[5,2,1,""]},"galaxy.app.Output":{to_CSV:[5,2,1,""],to_GeoJSON:[5,2,1,""],to_JSON:[5,2,1,""],to_dict:[5,2,1,""],to_list:[5,2,1,""]},"galaxy.app.TaskingManager":{extract_project_ids:[5,2,1,""],get_tasks_mapped_and_validated_per_user:[5,2,1,""],get_time_spent_mapping_and_validating_per_user:[5,2,1,""]},"galaxy.app.Training":{get_all_organisations:[5,2,1,""],get_trainingslist:[5,2,1,""]},"galaxy.app.Underpass":{all_training_organisations:[5,2,1,""],get_mapathon_summary_result:[5,2,1,""],training_list:[5,2,1,""]},"galaxy.app.UserStats":{get_statistics:[5,2,1,""],get_statistics_with_hashtags:[5,2,1,""],list_users:[5,2,1,""]},"galaxy.config":{get_db_connection_params:[5,4,1,""]},"galaxy.query_builder":{builder:[6,0,0,"-"]},"galaxy.query_builder.builder":{create_UserStats_get_statistics_query:[6,4,1,""],create_changeset_query:[6,4,1,""],create_hashtag_filter_query:[6,4,1,""],create_hashtagfilter_underpass:[6,4,1,""],create_osm_history_query:[6,4,1,""],create_timestamp_filter_query:[6,4,1,""],create_user_tasks_mapped_and_validated_query:[6,4,1,""],create_user_time_spent_mapping_and_validating_query:[6,4,1,""],create_users_contributions_query:[6,4,1,""],create_userstats_get_statistics_with_hashtags_query:[6,4,1,""],generate_data_quality_TM_query:[6,4,1,""],generate_data_quality_hashtag_reports:[6,4,1,""],generate_data_quality_username_query:[6,4,1,""],generate_filter_training_query:[6,4,1,""],generate_mapathon_summary_underpass_query:[6,4,1,""],generate_organization_hashtag_reports:[6,4,1,""],generate_training_organisations_query:[6,4,1,""],generate_training_query:[6,4,1,""]},"galaxy.validation":{models:[7,0,0,"-"]},"galaxy.validation.models":{BaseModel:[7,1,1,""],DataQualityHashtagParams:[7,1,1,""],DataQualityPointCollection:[7,1,1,""],DataQualityPointFeature:[7,1,1,""],DataQualityProp:[7,1,1,""],DataQuality_TM_RequestParams:[7,1,1,""],DataQuality_username_RequestParams:[7,1,1,""],DateStampParams:[7,1,1,""],EventType:[7,1,1,""],Frequency:[7,1,1,""],IssueType:[7,1,1,""],MapathonContributor:[7,1,1,""],MapathonDetail:[7,1,1,""],MapathonRequestParams:[7,1,1,""],MapathonSummary:[7,1,1,""],MappedFeature:[7,1,1,""],MappedFeatureWithUser:[7,1,1,""],MappedTaskStats:[7,1,1,""],OrganizationHashtag:[7,1,1,""],OrganizationHashtagParams:[7,1,1,""],OrganizationOutputtype:[7,1,1,""],OutputType:[7,1,1,""],Source:[7,1,1,""],TMUserStats:[7,1,1,""],TimeSpentMapping:[7,1,1,""],TimeSpentValidating:[7,1,1,""],TimeStampParams:[7,1,1,""],TopicType:[7,1,1,""],TrainingOrganisations:[7,1,1,""],TrainingParams:[7,1,1,""],Trainings:[7,1,1,""],User:[7,1,1,""],UserStatsParams:[7,1,1,""],UsersListParams:[7,1,1,""],ValidatedTaskStats:[7,1,1,""],checkIfDuplicates:[7,4,1,""],to_camel:[7,4,1,""]},"galaxy.validation.models.BaseModel":{Config:[7,1,1,""]},"galaxy.validation.models.BaseModel.Config":{alias_generator:[7,2,1,""],allow_population_by_field_name:[7,3,1,""],use_enum_values:[7,3,1,""]},"galaxy.validation.models.DataQualityHashtagParams":{check_not_defined_fields:[7,2,1,""],geometry:[7,3,1,""],hashtags:[7,3,1,""],issue_type:[7,3,1,""],output_type:[7,3,1,""]},"galaxy.validation.models.DataQualityPointCollection":{features:[7,3,1,""]},"galaxy.validation.models.DataQualityPointFeature":{geometry:[7,3,1,""],properties:[7,3,1,""]},"galaxy.validation.models.DataQualityProp":{Changeset_id:[7,3,1,""],Changeset_timestamp:[7,3,1,""],Issue_type:[7,3,1,""],Osm_id:[7,3,1,""]},"galaxy.validation.models.DataQuality_TM_RequestParams":{issue_types:[7,3,1,""],output_type:[7,3,1,""],project_ids:[7,3,1,""]},"galaxy.validation.models.DataQuality_username_RequestParams":{issue_types:[7,3,1,""],osm_usernames:[7,3,1,""],output_type:[7,3,1,""]},"galaxy.validation.models.DateStampParams":{check_timestamp_diffs:[7,2,1,""],from_timestamp:[7,3,1,""],to_timestamp:[7,3,1,""]},"galaxy.validation.models.EventType":{IN_PERSON:[7,3,1,""],VIRTUAL:[7,3,1,""]},"galaxy.validation.models.Frequency":{MONTHLY:[7,3,1,""],QUARTERLY:[7,3,1,""],WEEKLY:[7,3,1,""],YEARLY:[7,3,1,""]},"galaxy.validation.models.IssueType":{BAD_GEOM:[7,3,1,""],BAD_VALUE:[7,3,1,""],COMPLETE:[7,3,1,""],DUPLICATE:[7,3,1,""],INCOMPLETE:[7,3,1,""],NO_TAGS:[7,3,1,""],ORPHAN:[7,3,1,""],OVERLAPPING:[7,3,1,""]},"galaxy.validation.models.MapathonContributor":{editors:[7,3,1,""],total_buildings:[7,3,1,""],user_id:[7,3,1,""],username:[7,3,1,""]},"galaxy.validation.models.MapathonDetail":{contributors:[7,3,1,""],mapped_features:[7,3,1,""],tm_stats:[7,3,1,""]},"galaxy.validation.models.MapathonRequestParams":{check_hashtag_filter:[7,2,1,""],check_source:[7,2,1,""],hashtags:[7,3,1,""],project_ids:[7,3,1,""],source:[7,3,1,""]},"galaxy.validation.models.MapathonSummary":{mapped_features:[7,3,1,""],total_contributors:[7,3,1,""]},"galaxy.validation.models.MappedFeature":{action:[7,3,1,""],count:[7,3,1,""],feature:[7,3,1,""]},"galaxy.validation.models.MappedFeatureWithUser":{username:[7,3,1,""]},"galaxy.validation.models.MappedTaskStats":{tasks_mapped:[7,3,1,""],user_id:[7,3,1,""]},"galaxy.validation.models.OrganizationHashtag":{end_date:[7,3,1,""],frequency:[7,3,1,""],hashtag:[7,3,1,""],start_date:[7,3,1,""],total_new_buildings:[7,3,1,""],total_new_road_meters:[7,3,1,""],total_unique_contributors:[7,3,1,""]},"galaxy.validation.models.OrganizationHashtagParams":{check_date_difference:[7,2,1,""],check_hashtag_string:[7,2,1,""],end_date:[7,3,1,""],frequency:[7,3,1,""],hashtags:[7,3,1,""],output_type:[7,3,1,""],start_date:[7,3,1,""]},"galaxy.validation.models.OrganizationOutputtype":{CSV:[7,3,1,""],JSON:[7,3,1,""]},"galaxy.validation.models.OutputType":{CSV:[7,3,1,""],GEOJSON:[7,3,1,""]},"galaxy.validation.models.Source":{INSIGHT:[7,3,1,""],UNDERPASS:[7,3,1,""]},"galaxy.validation.models.TMUserStats":{tasks_mapped:[7,3,1,""],tasks_validated:[7,3,1,""],time_spent_mapping:[7,3,1,""],time_spent_validating:[7,3,1,""]},"galaxy.validation.models.TimeSpentMapping":{time_spent_mapping:[7,3,1,""],user_id:[7,3,1,""]},"galaxy.validation.models.TimeSpentValidating":{time_spent_validating:[7,3,1,""],user_id:[7,3,1,""]},"galaxy.validation.models.TimeStampParams":{check_timestamp_diffs:[7,2,1,""],from_timestamp:[7,3,1,""],to_timestamp:[7,3,1,""]},"galaxy.validation.models.TopicType":{FIELD:[7,3,1,""],OTHER:[7,3,1,""],REMOTE:[7,3,1,""]},"galaxy.validation.models.TrainingOrganisations":{id:[7,3,1,""],name:[7,3,1,""]},"galaxy.validation.models.TrainingParams":{check_timestamp_order:[7,2,1,""],event_type:[7,3,1,""],from_datestamp:[7,3,1,""],oid:[7,3,1,""],to_datestamp:[7,3,1,""],topic_type:[7,3,1,""]},"galaxy.validation.models.Trainings":{date:[7,3,1,""],eventtype:[7,3,1,""],hours:[7,3,1,""],location:[7,3,1,""],name:[7,3,1,""],organization:[7,3,1,""],tid:[7,3,1,""],topics:[7,3,1,""],topictype:[7,3,1,""]},"galaxy.validation.models.User":{user_id:[7,3,1,""],user_name:[7,3,1,""]},"galaxy.validation.models.UserStatsParams":{hashtags:[7,3,1,""],project_ids:[7,3,1,""],user_id:[7,3,1,""]},"galaxy.validation.models.UsersListParams":{from_timestamp:[7,3,1,""],to_timestamp:[7,3,1,""],user_names:[7,3,1,""]},"galaxy.validation.models.ValidatedTaskStats":{tasks_validated:[7,3,1,""],user_id:[7,3,1,""]},API:{BaseModel:[0,1,1,""],auth:[1,0,0,"-"],changesets:[2,0,0,"-"],countries:[3,0,0,"-"],data:[4,0,0,"-"],data_quality:[0,0,0,"-"],main:[0,0,0,"-"],mapathon:[0,0,0,"-"],organization:[0,0,0,"-"],osm_users:[0,0,0,"-"],to_camel:[0,4,1,""],trainings:[0,0,0,"-"]},galaxy:{DataQuality:[5,1,1,""],Database:[5,1,1,""],Mapathon:[5,1,1,""],Output:[5,1,1,""],app:[5,0,0,"-"],config:[5,0,0,"-"],query_builder:[6,0,0,"-"],validation:[7,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:function"},terms:{"case":[0,5],"class":[0,1,2,5,7],"enum":[2,7],"float":[2,7],"function":5,"int":[1,2,7],"return":[5,6,7],"static":5,"true":[0,5,7],If:7,It:5,Not:7,about:5,accept:7,access_token:1,action:7,activ:8,added_highwai:2,added_highway_km:2,addedhighwai:2,addedhighwaykm:2,after:5,alias_gener:[0,7],all:[5,6,7],all_training_organis:5,allow_population_by_field_nam:[0,7],along:5,an:[2,7],ani:7,api:[5,7,8,9],app:9,arg:7,arrai:7,auth:[0,9],authus:1,avail:5,avoid:5,bad_geom:7,bad_valu:7,badgeom:7,badvalu:7,base:[0,1,2,5,7],basemodel:[0,1,2,7],basi:6,bbox:7,becom:0,bool:5,builder:[5,9],callback:[1,4],camel:0,can:7,changeset:[0,6,9],changeset_id:7,changeset_queri:6,changeset_timestamp:7,changesetid:7,changesetresult:2,changesettimestamp:7,check:[5,7],check_date_differ:7,check_for_json:5,check_hashtag_filt:7,check_hashtag_str:7,check_not_defined_field:7,check_sourc:7,check_timestamp_diff:7,check_timestamp_ord:7,checkifdupl:7,classmethod:[2,7],close_conn:5,closs:5,column:5,column_nam:6,columnnam:6,complet:7,con:6,config:[0,7,9],conn:6,connect:5,constrainedlistvalu:7,contain:[5,7],content:9,contribut:[5,6],contributor:[2,7],convert:5,count:7,countri:[0,9],create_changeset_queri:6,create_hashtag_filter_queri:6,create_hashtagfilter_underpass:6,create_osm_history_queri:6,create_timestamp_filter_queri:6,create_user_tasks_mapped_and_validated_queri:6,create_user_time_spent_mapping_and_validating_queri:6,create_users_contributions_queri:6,create_userstats_get_statistics_queri:6,create_userstats_get_statistics_with_hashtags_queri:6,criteria:7,csv:[5,7],cur:6,current:5,data:[0,5,6,7,9],data_qu:[5,9],data_quality_hashtag_report:0,data_quality_report:0,databas:5,datafram:5,dataqu:[5,7],dataquality_tm_requestparam:7,dataquality_username_requestparam:[0,7],dataqualityhashtag:5,dataqualityhashtagparam:[0,5,7],dataqualitypointcollect:7,dataqualitypointfeatur:7,dataqualityprop:7,date:[2,7],datestamp:7,datestampparam:7,datetim:[2,7],db_name:4,db_param:5,dbidentifi:5,deleted_highwai:2,deleted_highway_km:2,deletedhighwai:2,deletedhighwaykm:2,depend:[0,1],descript:[5,7],detail:5,develop:8,dict:5,differ:7,document:5,duplic:7,editor:7,either:7,ellipsi:1,empti:7,end_dat:7,end_datetim:2,enddat:7,enddatetim:2,entiti:7,enumer:[2,7],err:5,error:5,event:[5,7],event_typ:7,eventtyp:7,except:5,execut:5,executequeri:5,exist:7,extract_project_id:5,fals:5,featur:7,featurecollect:7,field:7,file:5,fileloc:5,filter:6,filter_queri:6,filterparam:2,format:[0,5],frequenc:7,from:[5,6],from_datestamp:7,from_timestamp:[6,7],fromdatestamp:7,fromtimestamp:7,funtion:5,galaxi:0,gener:[5,6,7],generate_data_quality_hashtag_report:6,generate_data_quality_tm_queri:6,generate_data_quality_username_queri:6,generate_filter_training_queri:6,generate_mapathon_summary_underpass_queri:6,generate_organization_hashtag_report:6,generate_training_organisations_queri:6,generate_training_queri:6,genericmodel:7,geojson:[2,5,7],geojson_pydant:[2,7],geom:7,geom_filter_subqueri:2,geometri:[2,5,7],get:5,get_all_organis:5,get_changeset:2,get_countri:3,get_db_connection_param:5,get_detailed_report:5,get_mapathon_detailed_report:0,get_mapathon_detailed_result:5,get_mapathon_summari:0,get_mapathon_summary_result:5,get_ogranization_stat:0,get_organisations_list:0,get_report:5,get_report_as_csv:5,get_statist:5,get_statistics_with_hashtag:5,get_summari:5,get_tasks_mapped_and_validated_per_us:5,get_time_spent_mapping_and_validating_per_us:5,get_trainings_list:0,get_trainingslist:5,ha:5,handl:5,hashtag:[2,5,6,7],hastag:6,header:1,hello_world_goodbye_new_york:0,helloworldgoodbyenewyork:0,henc:5,histori:6,hour:7,humanitarian:8,id:[1,5,7],img_url:1,in_person:7,includ:5,incomplet:7,index:8,individu:5,inperson:7,input:5,input_list:7,inputtyp:5,insid:5,insight:[5,7],instanc:5,integ:7,intuit:8,iso3:2,issu:7,issue_typ:7,issuetyp:7,json:[5,7],kwarg:[2,7],lat:5,lat_column:5,leak:5,librari:8,list:[5,6,7],list_us:[0,5],lng:5,lng_column:5,locat:[5,7],login:1,login_requir:[0,1],login_url:[1,4],m:7,main:[1,5,7,9],manag:[5,7],mapathon:[5,6,7,9],mapathoncontributor:7,mapathondetail:7,mapathonrequestparam:[0,7],mapathonsummari:7,mapped_featur:7,mappedfeatur:7,mappedfeaturewithus:7,mappedtaskstat:7,matching_typ:2,meant:5,memori:5,method:5,model:[0,5,9],modified_highwai:2,modified_highway_km:2,modifiedhighwai:2,modifiedhighwaykm:2,modul:[8,9],monthli:7,my_data:1,name:[2,5,7],need:5,no_tag:7,none:[2,5,7],notag:7,note:7,object:[0,5,7],offer:8,oid:[5,7],onli:[5,7],openstreetmap:8,option:[2,7],order:7,organ:[5,7,9],organis:[5,6],organiz:0,organizationhashtag:[5,7],organizationhashtagparam:[0,5,7],organizationoutputtyp:7,orphan:7,osm:[5,6],osm_id:7,osm_us:9,osm_usernam:7,osmid:7,osmusernam:7,other:7,otherwis:5,out:[6,7],output:[5,7],output_file_path:5,output_typ:7,outputtyp:7,overlap:7,packag:[8,9],page:[5,8],panda:5,param:[0,2,5,6],paramet:[5,7],parameter:[6,7],pars:5,part:8,path:5,payload:5,point:[5,7],polygon:[2,7],polygonfilt:2,post:7,predefin:7,print:5,print_psycopg2_except:5,project:[5,7,8],project_id:[6,7],projectid:7,prop:7,properti:7,provid:[5,6,7],psycopg2:5,pydant:[0,1,7],python:8,q:7,qualiti:[5,6,7],quarterli:7,queri:[5,6],query_build:[5,9],query_result:5,rais:7,relat:5,remot:7,report:5,request:[1,4,7],requir:[5,7],respons:[0,5],respos:5,result:5,result_str:5,router:[0,9],run:5,search:8,self:5,seper:0,should:7,simpl:8,skill:7,so:0,sourc:[5,7],specif:5,specifi:5,sql:5,src:[0,8],starlett:[1,4],start_dat:7,start_datetim:2,startdat:7,startdatetim:2,str:[0,1,2,4,7],string:[0,5,7],submodul:9,subpackag:9,success:5,summari:5,support:[5,7],tabl:6,take:5,task:[5,7],taskingmanag:5,tasks_map:7,tasks_valid:7,tasksmap:7,tasksvalid:7,test:5,thi:[0,5,8],tid:7,time_spent_map:7,time_spent_valid:7,timespentmap:7,timespentvalid:7,timestamp:[6,7],timestampparam:7,timestap:7,tm:[5,6],tm_stat:7,tmstat:7,tmuserstat:7,to_camel:[0,7],to_csv:5,to_csv_stream:5,to_datestamp:7,to_dict:5,to_geojson:5,to_json:5,to_list:5,to_timestamp:[6,7],todatestamp:7,token:1,topic:7,topic_typ:7,topictyp:7,total:5,total_build:7,total_changeset:2,total_contributor:7,total_new_build:7,total_new_road_met:7,total_unique_contributor:7,totalbuild:7,totalchangeset:2,totalcontributor:7,totalnewbuild:7,totalnewroadmet:7,totaluniquecontributor:7,totimestamp:7,train:[5,6,7,9],training_list:5,trainingorganis:7,trainingparam:[0,5,7],tupl:7,type:[2,5,7],under:[7,8],underpass:[5,6,7],underscor:0,union:[2,7],unprocess:7,url:1,us:[5,7],use_enum_valu:7,user:[5,6,7],user_data:[0,1],user_id:7,user_nam:7,user_statist:0,userid:7,usernam:[1,5,6,7],userslistparam:[0,7],userstat:5,userstatsparam:[0,7],util:[0,9],v:2,valid:[0,5,9],validatedtaskstat:7,valu:[2,7],valueerror:7,virtual:7,w:7,we:7,weekli:7,where:5,with_usernam:6,within:5,word:0,y:7,yearli:7,you:5,your:5},titles:["API package","API.auth package","API.changesets package","API.countries package","API.data package","galaxy package","galaxy.query_builder package","galaxy.validation package","Welcome to OSM Galaxy\u2019s documentation!","Galaxy"],titleterms:{api:[0,1,2,3,4],app:5,auth:1,builder:6,changeset:2,config:5,content:[0,1,2,3,4,5,6,7,8],countri:3,data:4,data_qu:0,document:8,galaxi:[5,6,7,8,9],indic:8,main:0,mapathon:0,model:7,modul:[0,1,2,3,4,5,6,7],organ:0,osm:8,osm_us:0,packag:[0,1,2,3,4,5,6,7],query_build:6,router:[1,2,3,4],s:8,submodul:[0,1,2,3,4,5,6,7],subpackag:[0,5],tabl:8,train:0,util:2,valid:7,welcom:8}})