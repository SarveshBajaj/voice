using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;


public class WebRequestHandler : MonoBehaviour
{
    #region public fields
        public Text ResultText;
        public int RequestTimeout = 30;
    #endregion

    #region private fields
        private string requestUrl = "http://localhost:5000/uploadfile";
        private int lastCount;
    #endregion

    #region public methods
        public void AnalyseSlice(string filename,int count){
            StartCoroutine(sendAnalysisRequest(filename,count));
            if(count == 0){
                lastCount = 0;
            }
        }
    #endregion
    
    #region monobehaviour callbacks
        
    #endregion

    #region private methods

       

        IEnumerator sendAnalysisRequest(string filename,int count){
            if(!filename.EndsWith(".wav")){
                filename+=".wav";
            }
            byte[] slicedclip = File.ReadAllBytes(Application.dataPath + "/audio/"+filename);
            WWWForm form = new WWWForm();
            form.AddBinaryData("file", slicedclip, filename, "audio/wav");
            UnityWebRequest request = UnityWebRequest.Post(requestUrl, form);
            request.timeout=RequestTimeout;
            yield return request.SendWebRequest();
            Debug.Log("request completed with code: " + request.responseCode);
            if(request.isNetworkError) {
                Debug.Log("Request No: " + count.ToString());
                Debug.Log("Error: " + request.error);
            }
            else {
                Debug.Log("Request No: " + count.ToString());
                Debug.Log("Request Response: " + request.downloadHandler.text);
                var values = request.downloadHandler.text;
                if(count>=lastCount){
                    lastCount = count;
                    showResults(values);
                }
            }
        }

        void showResults(string values){
            string text = "count:"+lastCount+"\n";
            text+=values;
            ResultText.text = text;
        }
    #endregion
}
