using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System.IO;
public class RecorderScript : MonoBehaviour
{
    #region private fields
        private bool micConnected = false;  
        private bool isRecording = false;
        //The maximum and minimum available recording frequencies  
        private int minFreq;  
        private int maxFreq;  
    
        //A handle to the attached AudioSource  
        private AudioClip mainClip;

        private int sampleoffset;

        private List<AudioClip> slicedClips;  

        private float[] slice;
    #endregion

    #region public fields

        public int sliceSize = 5;
        public AudioSource audioSource;

        public Text status;
    #endregion
    
    #region Monobehaviour callbacks
        //Use this for initialization  
        void Start()   
        {  
            status.text = "standby ...";

            //Check if there is at least one microphone connected  
            if(Microphone.devices.Length <= 0)  
            {  
                //Throw a error message at the console if there isn't  
                Debug.LogError("Microphone not connected!");  
            }  
            else //At least one microphone is present  
            {  
                //Set 'micConnected' to true  
                micConnected = true;  
    
                //Get the default microphone recording capabilities  
                Microphone.GetDeviceCaps(null, out minFreq, out maxFreq);  
    
                //According to the documentation, if minFreq and maxFreq are zero, the microphone supports any frequency...  
                if(minFreq == 0 && maxFreq == 0)  
                {  
                    //...meaning 44100 Hz can be used as the recording sampling rate  
                    maxFreq = 44100;  
                }  
    
            }  
        }  
        
    #endregion
    
    #region eventHandler methods
        public void onRecordPressed(){
            if(!isRecording){
                //delete existing files
                clearSavingDirectory();

                isRecording = true; 
                mainClip = Microphone.Start(null, true, 20, maxFreq);
                StartCoroutine(sliceClips());
                status.text = "recording ...";
            }
            else{
                isRecording = false;
                Microphone.End(null);
                StopCoroutine(sliceClips());
                status.text = "standby ...";
                SavWav.Save("main",mainClip);

            }
        }
        public void onPlayMainPressed(){
            if(isRecording){
                isRecording = false;
                Microphone.End(null);
                StopCoroutine(sliceClips());
                SavWav.Save("main",mainClip);
 
            }
            if(!audioSource.isPlaying){
                audioSource.clip = mainClip;
                audioSource.Play();
                status.text = "playing ...";
            }
            else
            {
                audioSource.Stop();
                status.text = "standby ...";
            }
        }

    #endregion

    #region private methods
        IEnumerator sliceClips(){
            sampleoffset=0;
            int count = 0;
            while(isRecording){
                yield return new WaitForSecondsRealtime(sliceSize);
            
            int freq = mainClip.frequency;
            int ch = mainClip.channels;
            slice = new float[sliceSize*freq*ch];
            
            mainClip.GetData(slice,sampleoffset);
            
            sampleoffset+=slice.Length;
            AudioClip slicedClip = AudioClip.Create("slicedClip",slice.Length,ch,freq,false);
            slicedClip.SetData(slice,0);
           // slicedClips.Add(slicedClip);
            SavWav.Save("slice"+count++.ToString(),slicedClip);
            }
            

        }

        void clearSavingDirectory(){
            DirectoryInfo d = new DirectoryInfo(Application.persistentDataPath);
            FileInfo[] files = d.GetFiles();
            foreach (FileInfo file in files)
            {
                if(file.Name.EndsWith(".wav")){
                    File.Delete(file.FullName);
                }                
            }
        }
    #endregion
    

}
