import os
import platform
import subprocess

system_os = platform.system()

def m4v_to_mp4(m4v_url):
    m4v_path = os.getcwd()
    mp4_path = os.getcwd()
    # print("videpo path is", m4v_path, mp4_path)

    if system_os == "Windows":
        m4v_path = os.path.join(m4v_path, r'storage\content\videos\m4v')
        mp4_path = os.path.join(mp4_path, r'storage\content\videos\mp4')
        m4v_filename = m4v_url.split('\\')[-1]
        m4v_path = os.path.join(m4v_path, m4v_filename)
        mp4_filename = m4v_filename.replace('.m4v', '.mp4')
        mp4_path = os.path.join(mp4_path, mp4_filename)
    else:
        m4v_path = os.path.join(m4v_path, 'storage/content/videos/m4v')
        # print("m4v_path ", m4v_path)
        mp4_path = os.path.join(mp4_path, 'storage/content/videos/mp4')
        m4v_filename = m4v_url.split('/')[-1]
        # print("m4v_filename ", m4v_filename)
        m4v_path = os.path.join(m4v_path, m4v_filename)
        mp4_filename = m4v_filename.replace('.m4v', '.mp4')
        mp4_path = os.path.join(mp4_path, mp4_filename)
        
    if not os.path.exists(mp4_path):
        try:
            command = ["ffmpeg", "-i", m4v_path, "-vcodec", "copy", "-acodec", "copy", mp4_path]
            subprocess.check_call(command)
            print("Successfully converted m4v file to mp4")
        except subprocess.CalledProcessError:
            print("Problem converting " + m4v_url)
            return None

    # print("final path is ", mp4_path.split('/')[-1])
    return mp4_path.split('/')[-1]

# m4v_to_mp4(r"C:\contentservermech\contentserver\pos\static\storage\content\videos\m4v\07_RANI_MACCHHLEE_HB_202005261804388793.m4v")


def wav_to_mp3(wav_url):
    wav_path = os.getcwd()
    mp3_path = os.getcwd()
    # print(wav_path, mp3_path)

    if system_os == "Windows":
        wav_path = os.path.join(wav_path, r'storage\content\audios\wav')
        mp3_path = os.path.join(mp3_path, r'storage\content\audios\mp3')
        wav_filename = wav_url.split('\\')[-1]
        wav_path = os.path.join(wav_path, wav_filename)
        mp3_filename = wav_filename.replace('.wav', '.mp3')
        mp3_path = os.path.join(mp3_path, mp3_filename)
    else:
        wav_path = os.path.join(wav_path, 'storage/content/audios/wav')
        mp3_path = os.path.join(mp3_path, 'storage/content/audios/mp3')
        wav_filename = wav_url.split('/')[-1]
        wav_path = os.path.join(wav_path, wav_filename)
        mp3_filename = wav_filename.replace('.wav', '.mp3')
        mp3_path = os.path.join(mp3_path, mp3_filename)
        
    if not os.path.exists(mp3_path):
        try:
            command = ["ffmpeg", "-i", wav_path, "-acodec", "mp3", "-ac", "2",
                       "-ab", "64k", "-y", "-hide_banner", "-loglevel", "warning", mp3_path]
            subprocess.check_call(command)
            print("Successfully converted wav file to mp3")
        except subprocess.CalledProcessError:
            print("Problem converting " + wav_url)
            return None

    # print("final path is ", mp3_path)
    return mp3_path


# wav_to_mp3(r"C:\contentservermech\contentserver\pos\static\storage\content\audios\wav\Checklist_after_coming_home_HN_202006261809074910.wav")
