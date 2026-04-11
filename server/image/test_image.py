import torch
from diffusers import DiffusionPipeline

# switch to "mps" for apple devices
pipe = DiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", dtype=torch.bfloat16, device_map="cuda")

# prompt = "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"
prompt = "A sequence of tiger hunting in jungle, stalking to pouncing to taking down prey, warm color palette, muted colors, highly detailed, 8k, photorealistic, national geographic style, multiple action phases"
images = pipe(prompt, num_images_per_prompt=2).images
for i in range(len(images)):
    images[i].save(f"tigers{i}.png")

