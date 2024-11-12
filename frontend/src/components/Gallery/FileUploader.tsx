import React, { useState, useContext } from 'react';
import { postFile } from '../../services/api/postFile';
import { AuthContext } from '../../contexts/Auth';
import { AxiosProgressEvent } from 'axios';

const FileProgress = ({ file, progress }: { file: File; progress: number }) => (
  <div style={{ marginBottom: '10px' }}>
    <div>{file.name}</div>
    <progress className="w-full" value={progress} max="100"></progress>
  </div>
);

const FileUploader = () => {
  const authContext = useContext(AuthContext);
  const [files, setFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState<Record<string, number>>({});

  // Track the upload progress of each file
  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const onUploadProgress = (event: AxiosProgressEvent) => {
      if (event.lengthComputable) {
        const percentComplete = Math.round((event.loaded / event.total) * 100);
        setProgress((prevProgress) => ({
          ...prevProgress,
          [file.name]: percentComplete,
        }));
      }
    };

    try {
      await postFile(authContext, formData, onUploadProgress); // Use your postFile function to upload
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const selectedFiles = Array.from(event.target.files);
      setFiles((prevFiles) => [...prevFiles, ...selectedFiles]);

      selectedFiles.forEach((file) => {
        setProgress((prevProgress) => ({ ...prevProgress, [file.name]: 0 }));
        handleFileUpload(file);
      });
    }
  };

  return (
    <div>
      <input type="file" multiple onChange={handleFileSelect} />
      <div style={{ marginTop: '10px' }}>
        {files.map((file) => (
          <FileProgress
            key={file.name}
            file={file}
            progress={progress[file.name] || 0}
          />
        ))}
      </div>
    </div>
  );
};

export { FileUploader };
