import { callApi } from '../../utils/api'; // Adjust path to where your callApi is located
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';
import { AxiosProgressEvent } from 'axios';

const API_ENDPOINT = '/galleries/{gallery_id}/upload/'; // Adjust to your actual file upload endpoint
const API_METHOD = 'post';

type PostFileResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postFile(
  authContext: AuthContextType,
  galleryId: components['schemas']['Gallery']['id'],
  file: FormData, // FormData for file uploads
  onUploadProgress: (progressEvent: AxiosProgressEvent) => void // This is the upload progress callback
): Promise<ApiResponse<PostFileResponses[keyof PostFileResponses]>> {
  // Use the callApi function to perform the request
  return await callApi<
    PostFileResponses[keyof PostFileResponses],
    FormData // We are sending FormData which contains the file(s)
  >({
    url: API_ENDPOINT.replace('{gallery_id}', galleryId.toString()), // Replace the gallery_id with the actual gallery id
    method: API_METHOD,
    authContext,
    data: file,
    onUploadProgress: onUploadProgress, // Pass the progress callback to track the upload progress
  });
}

export { postFile, PostFileResponses };
