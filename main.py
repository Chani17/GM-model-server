from fastapi import FastAPI, File
import os
from starlette.config import Config
import requests
from zipfile import ZipFile
from pydantic import BaseModel
from gmModel_DC.generate import generate_dcgan
from gmModel_DC.train import train_dcgan

app = FastAPI()


config = Config(".env")
SERVER_IP = config('API_BASE_URL')


@app.get("/")
async def root():
    return {"hello"}


class File(BaseModel):
    email : str
    projectName : str
    zipUrl: str


# 클라우드 zip 파일 URL 가져오기
@app.post("/get/url")
async def download_and_extract(item: File):
    projectName = item.projectName
    email = item.email
    zipUrl = item.zipUrl
    print( projectName, email  , zipUrl)

    target_dir = 'user_dataset/'+projectName
    target_dir2 = 'gmModel_DC/user_dataset/'+projectName

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if not os.path.exists(target_dir2):
        os.makedirs(target_dir2)

    # HTTP GET 요청을 보내 파일 다운로드
    response = requests.get(item.zipUrl)
    if response.status_code != 200:
        raise Exception("Can't download a file.")
    

    file_path = os.path.join(target_dir, projectName+'_dataset.zip')
    file_path2 = os.path.join(target_dir2, projectName+'_dataset.zip')

    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(response.content)

    # 압축 해제
    with ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    #다운받은 zip 파일 삭제
    os.remove(file_path)

    # 파일 저장
    with open(file_path2, "wb") as f:
        f.write(response.content)

    # 압축 해제
    with ZipFile(file_path2, "r") as zip_ref:
        zip_ref.extractall(target_dir2)

    #다운받은 zip 파일 삭제
    os.remove(file_path2)

    await train_dcgan(projectName)
    await generate_images(projectName, email)


#이미지 생성 + zip 파일로 압축
async def generate_images(projectName, email):
    try:
        await generate_dcgan(projectName)

        output_dir = 'gmModel_DC/outputs/'+projectName
        zip_file_path = os.path.join(output_dir, projectName+'.zip')

        with ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(output_dir+'/generated_images'):
                print("zip 파일 생성 하는 중")
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, output_dir))

        await send_zip_fun(projectName, email)


    except Exception as e:
        return f"An error occurred: {str(e)}"
    
    return {"message": "done", "zip_filename": zip_file_path}


async def get_metrics(projectName, email):
    accuracy = 1
    fid = 1
    lpips = 1

#loss, generated_gif
async def send_zip_fun(projectName, email):
    output_dir = 'gmModel_DC/outputs/'+projectName + '/'
    zip_file_path = output_dir + projectName + '.zip'
    loss_fig_path = output_dir+ 'fig/Training_loss.png'
    gif_path = output_dir+ 'gif/X_ray.gif'
    generated_single_img_path = output_dir + 'generated_single_image.png'
    endpoint = SERVER_IP + "zips"

    data = {
        #원본, 생성
        "accuracy_generated": [93.2, 86.7],
        "accuracy_original_generated": [93.2, 91.3],
        "fid": [30.5, 125.9], 
        "LPIPS": [0.4, 0.23], 
        "email": email,
        "projectName": projectName
    }

    files = {
        "zipFile": (os.path.basename(zip_file_path), open(zip_file_path, "rb")),
        "loss": (os.path.basename(loss_fig_path), open(loss_fig_path, "rb")),
        "generated_gif": (os.path.basename(gif_path), open(gif_path, "rb")),
        "generated_single_img": (os.path.basename(generated_single_img_path), open(generated_single_img_path, "rb")),
    }

    response = requests.post(endpoint, files=files, data=data)


    if response.status_code == 200:
        return {"message": "Zip 파일을 성공적으로 보냈습니다."}
    else:
        return {"message": "Zip 파일 전송에 실패했습니다."}
    