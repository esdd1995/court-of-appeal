import logging
import os
import io

from django.http import HttpResponseBadRequest, StreamingHttpResponse, HttpResponseNotFound


from rest_framework import permissions
from rest_framework import generics

LOGGER = logging.getLogger(__name__)
no_record_found = "No record found."

class FillablePdfView(generics.GenericAPIView):
    
    permission_classes = (permissions.IsAuthenticated,)


    def extract_file_name(self, name):
        files = [
            {"file":"_CA-book_cover_page_template_2022-05-02-Final-draft",                                            "name":"ca-cover-page"},
            {"file":"_Written-argument-general-2022-05-02-Final-draft",                                               "name":"written-argument", },

            {"file":"E-Completion_Instructions_Appeal-Book-2022-05-09-Final-draft",                                   "name":"e-appeal-book"},
            {"file":"E-Completion_Instructions_Appeal-Record-2022-05-09-Final-draft",                                 "name":"e-appeal-record"},
            {"file":"E-Completion_Instructions_Application-Response-Books-Leave-Stay-2022-05-05-Final-draft",         "name":"e-application-leave-stay"},
            {"file":"E-Completion_Instructions_Application-Response-Books-Security-Costs-2022-05-05-Final-draft",     "name":"e-security-costs"},
            {"file":"E-Completion_Instructions_Application-Response-Books-Vary-2022-05-05-Final-draft",               "name":"e-vary"},
            {"file":"E-Completion_Instructions_Book-of-Authorities-2022-05-06-Final-draft",                           "name":"e-auth-book"},
            {"file":"E-Completion_Instructions-all-Factums-Replies-draft-2022-05-03-Final-draft",                     "name":"e-factum"},
            {"file":"Factum_respondent-draft-2022-04-22",                                                             "name":"factum-response"},

            {"file":"Paper-Completion_Instructions_Appeal-Book-2022-05-09-Final-draft",                               "name":"paper-appeal-book"},            
            {"file":"Paper-Completion_Instructions_Appeal-Record-2022-05-09-Final-draft",                             "name":"paper-appeal-record"},
            {"file":"Paper-Completion_Instructions_Application-Response-Books-Leave-Stay-2022-05-05-Final-draft",     "name":"paper-application-leave-stay"},            
            {"file":"Paper-Completion_Instructions_Application-Response-Books-Security-Costs-2022-05-05-Final-draft", "name":"paper-security-costs"},            
            {"file":"Paper-Completion_Instructions_Application-Response-Books-Vary-2022-05-05-Final-draft",           "name":"paper-vary"},
            {"file":"Paper-Completion_Instructions_CONDENSED-Book-of-Authorities-2022-05-09-Final-draft",             "name":"paper-condensed-auth-book"},                        
            {"file":"Paper-Completion_Instructions_CONDENSED-Evidence-Book-2022-05-09-Final-draft",                   "name":"paper-condensed-evidence-book"},
            {"file":"Paper-Completion_Instructions-all-Factums-Replies-draft-2022-05-03-Final-draft",                 "name":"paper-factum"}
            # {"file":"Paper-Completion_Instructions_Book-of-Authorities-2022-05-06-Final-draft",                       "name":"paper-auth-book"},
        ]
        return [fileitem["file"] for fileitem in files if fileitem["name"]==name]
        
    def get(self, request):
       
        name = request.query_params.get("name")
        if name is None:
            return HttpResponseBadRequest("Missing parameters.")

        file_name = self.extract_file_name(name)        
        if len(file_name)==1:
            filepath = os.getcwd()+'/api/fillable_files/'+file_name[0]+'.docx'
        else:
            return HttpResponseNotFound("File not found")


        with open(filepath, "rb") as file:
            docx_file = io.BytesIO(file.read())
            docx_file.seek(0)
       
        response = StreamingHttpResponse(
            streaming_content=docx_file,
            content_type='application/docx'
        )

        response['Content-Disposition'] = 'attachment;filename=file.docx'
        response["Content-Encoding"] = 'UTF-8'

        return response


   