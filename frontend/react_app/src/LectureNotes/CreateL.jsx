import LHeader from "./LHeader"
import styles from "./CreateL.module.css"
import Footer from '../ui/Footer'
import React, { useState, useRef } from "react";
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify';


const CreateL = () => {
  const [recording, setRecording] = useState(false);
  const [notes, setNotes] = useState("");
  const [uploadLoading, setUploadLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const mimeTypeRef = useRef("audio/webm")
  const navigate = useNavigate();
  const [paused, setPaused] = useState(false)
  const [hasRecording, setHasRecording] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [recordingProcessing, setRecordingProcessing] = useState(false);
  

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    const allowedTypes = [
      "audio/webm",
      "audio/wav",
      "audio/mpeg",
      "audio/mp4",
      "audio/x-m4a",
      "audio/ogg",
    ];

    // Check file format
    if (!allowedTypes.includes(file.type)) {
      toast.error(
        "Unsupported audio format. Please upload MP3, WAV, M4A, OGG, or WebM."
      );

      event.target.value = "";
      return;
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      toast.error(
        "Audio file is too large. Maximum allowed size is 50 MB."
      );

      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };





const handleUpload = async () => {
  if (!selectedFile) {
    toast("Please select an audio file first.");
    return;
  }

  if (selectedFile.size > MAX_FILE_SIZE) {
    toast.error(
      "Audio file is too large. Maximum allowed size is 50 MB."
    );
    return;
  }

  
  setUploading(true);
  setUploadProgress(0);

  const formData = new FormData();
  formData.append("audio", selectedFile);

  const token = localStorage.getItem("access");

  const xhr = new XMLHttpRequest();

  // Upload progress
  xhr.upload.addEventListener("progress", (event) => {
    if (event.lengthComputable) {
      const percent = Math.round(
        (event.loaded / event.total) * 100
      );

      setUploadProgress(percent);
    }
  });

  xhr.addEventListener("load", () => {
    setUploading(false);

    let data = {};

    try {
      data = JSON.parse(xhr.responseText);
    } catch (error) {
      console.error("Invalid server response:", error);
    }

    if (xhr.status >= 200 && xhr.status < 300) {
      const lectureId = data.lecture_id;

      if (!lectureId) {
        toast.error("No lecture ID returned.");
        setUploadLoading(false);
        return;
      }

      setUploadProgress(100);
      setProcessing(true);

      toast.success(
        "Audio uploaded successfully. Processing lecture..."
      );

      checkStatus(lectureId);

    } else {
      toast.error(
        data.detail ||
        data.error ||
        "Unable to upload audio."
      );

      
      setUploadLoading(false);
      setUploadProgress(0);
    }
  });

  xhr.addEventListener("error", () => {
    setUploadLoading(false)
    setUploadProgress(0);

    toast.error(
      "Upload failed. Please check your connection and try again."
    );
  });

  xhr.addEventListener("abort", () => {
    setUploadLoading(false)
    setUploadProgress(0);

    toast.error("Upload cancelled.");
  });

  xhr.open(
    "POST",
    "https://smartnoteapi.onrender.com/api/notes/upload-audio/"
  );

  xhr.setRequestHeader(
    "Authorization",
    `Bearer ${token}`
  );

  xhr.send(formData);
};


  

  const checkStatus = (lectureId) => {
  const interval = setInterval(async () => {
    try {
      const res = await fetch(
        `https://smartnoteapi.onrender.com/api/notes/lectures/${lectureId}/status/`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access")}`,
          },
        }
      );

      const data = await res.json();

      console.log("Status:", data.status);

      if (data.status === "completed") {
        clearInterval(interval);

        setUploadLoading(false);
        setRecordingProcessing(false);

        navigate(`/viewlecture/${lectureId}`);
      }

      if (data.status === "failed") {
        clearInterval(interval);

        setUploadLoading(false);
        setRecordingProcessing(false);

        toast.error("Processing failed");
      }

    } catch (err) {
      console.error("Polling error:", err);

      clearInterval(interval);

      setUploadLoading(false);
      setRecordingProcessing(false);

      toast.error(
        "Unable to check lecture processing status."
      );
    }

  }, 3000);
};


  const handleRecordClick = async () => {
  
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    toast("Recording not supported on this device/browser");
    return;
  }
  
  if (!recording) {
    
    const mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/mp4"
    mimeTypeRef.current = mimeType;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream, { mimeType });
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };
    mediaRecorder.start();
    setRecording(true);
    setPaused(false);
  } else if (!paused) {
    
    mediaRecorderRef.current.pause();
    setPaused(true);
  } else {
    
    mediaRecorderRef.current.resume();
    setPaused(false);
  }
};
const handleStop = () => {
  if (mediaRecorderRef.current) {
    mediaRecorderRef.current.stop();
    setRecording(false);
    setPaused(false);
    setHasRecording(true);
  }
};
const handleSubmit = async () => {
  if (audioChunksRef.current.length === 0) {
    toast("No recording available");
    return;
  }

  setUploadLoading(true);
  setRecordingProcessing(true);

  const audioBlob = new Blob(audioChunksRef.current, {
    type: mimeTypeRef.current,
  });
  const formData = new FormData();
  formData.append("audio", audioBlob, "lecture.webm");

  try {
    const token = localStorage.getItem("access");
    const response = await fetch("https://smartnoteapi.onrender.com/api/notes/upload-audio/", {
      method: "POST",
      body: formData,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    const data = await response.json();
    const lectureId = data.lecture_id;

    if (!lectureId) {
      toast("No lecture ID returned");
      setUploadLoading(false)
      setRecordingProcessing(false);
      return;
    }

    checkStatus(lectureId);
  } catch (error) {
    const message = error?.response?.data?.detail || "Unable to create lecture.";
    toast(message);
    setUploadLoading(false)
    setRecordingProcessing(false);
  }
};

return (
    <>
      <div className={styles.create_con}>
        <LHeader />
        <div className={styles.create}>
          <div className={styles.message}>
            <p className={styles.text}>
              Click the start button to record your lectures and turn them into lectures notes using AI
            </p>
            <div className={`${styles.record} ${recording ? styles.animate : ""}`}>
              <span></span>
            </div>

          <div className={styles.btn}>

            <button
              onClick={handleRecordClick}
              className={styles.createLBtn}
              disabled={recordingProcessing}
            >
              {!recording
                ? "Start"
                : paused
                  ? "Resume"
                  : "Pause"}
            </button>

            {recording && (
              <button
                onClick={handleStop}
                className={styles.deleteBtn}
              >
                Stop
              </button>
            )}

            {!recording && hasRecording && (
              <button
                onClick={handleSubmit}
                className={styles.deleteBtn}
                disabled={recordingProcessing}
              >
                Submit
              </button>
            )}

            {recordingProcessing && (
              <div className={styles.recordingLoaderContainer}>
                <div className={styles.loader}></div>

                <p className={styles.convert}>
                  Converting your recording into lecture notes...
                </p>
              </div>
            )}

            {uploading && (
              <div className={styles.loader}></div>
            )}

            <div className={styles.uploadSection}>

              <div className={styles.uploadIcon}>
                ↑
              </div>

              <h3 className={styles.uploadTitle}>
                Upload Existing Lecture
              </h3>

              <p className={styles.uploadText}>
                Have a recorded audio already?
                <br />
                Upload it and let SmartNotes convert it into structured notes.
              </p>

              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />

              <button
                type="button"
                onClick={() => fileInputRef.current.click()}
                className={styles.uploadChooseBtn}
              >
                Choose Audio File
              </button>

              <p className={styles.supportedFormats}>
                MP3 • WAV • M4A • OGG • WebM
              </p>

              {selectedFile && (
                <div className={styles.selectedFile}>
                  <span className={styles.fileIcon}>♪</span>

                  <div className={styles.fileInfo}>
                    <span className={styles.fileName}>
                      <p className={styles.selectedFile}>
                        Selected: {selectedFile.name}
                        <br />
                        Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </span>

                    <span className={styles.fileSize}>
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </span>
                  </div>
                </div>
              )}
              {uploading && (
                <div className={styles.uploadProgressContainer}>

                  <div className={styles.progressHeader}>
                    <span>Uploading audio...</span>
                    <span>{uploadProgress}%</span>
                  </div>

                  <div className={styles.progressTrack}>
                    <div
                      className={styles.progressBar}
                      style={{
                        width: `${uploadProgress}%`
                      }}
                    ></div>
                  </div>

                </div>
              )}

              {processing && (
                <div className={styles.processingMessage}>
                  <div className={styles.processingSpinner}></div>

                  <p className={styles.convert}>
                    Converting your audio into lecture notes...
                  </p>

                  <span>
                    This may take a little while.
                  </span>
                </div>
              )}

              {selectedFile && !uploading && (
                <button
                  type="button"
                  onClick={handleUpload}
                  className={styles.uploadConvertBtn}
                >
                  Upload & Convert
                </button>
              )}

            </div>




            </div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default CreateL;















