import click
import imageio
import numpy as np
import praw
import os
import random
import shutil
import tempfile
import textwrap
import urllib
from PIL import Image, ImageFont, ImageDraw, ImageFilter

@click.command()
@click.option('--source_txt', default='showerthoughts',
    help='Subreddit source of captions', show_default=True)
@click.option('--source_img', default='earthporn',
    help='Subreddit source of images', show_default=True)
@click.option('--n_imgs', default=10,
    help='Number of output images', show_default=True)
@click.option('--line_length', default=48,
    help='Caption line length', show_default=True)
@click.option('--no_portraits', is_flag=True,
    help='Don\' include portrait aspect ratio (width < height)', show_default=True)
@click.option('--no_landscapes', is_flag=True,
    help='Don\'t include landscape aspect ratio (width > height)', show_default=True)
@click.option('--nsfw_ok', is_flag=True,
    help='Include NSFW (not safe for work) content', show_default=True)
@click.option('--quote_location', type=click.Choice(['bottom', 'middle', 'top']), default='bottom',
    help='Quote vertical location', show_default=True)
@click.option('--font_url', default='https://github.com/google/fonts/raw/master/ofl/kadwa/Kadwa-Bold.ttf',
    help='URL of the font file', show_default=True)
@click.option('--out_path', default='output',
    help='Output path', show_default=True)
@click.option('--clear_before_output', is_flag=True,
    help='Empty output folder before generating output', show_default=True)
def _click_main(source_txt, source_img, n_imgs, line_length, no_portraits,
    no_landscapes, nsfw_ok, quote_location, font_url, out_path, clear_before_output):
    r = praw.Reddit('imgtxtmashup memegen')

    # Load the font
    font_path = os.path.join('fonts', font_url.split('/')[-1])
    if not os.path.isfile(font_path):
        resp = urllib.request.urlopen(font_url)
        os.makedirs(os.path.dirname(font_path), exist_ok=True)
        with open(font_path, 'wb') as font_file:
            font_file.write(resp.read())
    else:
        with open(font_path, 'rb') as font_file:
            pass

    # Grab the submissions
    txt_subreddit = r.get_subreddit(source_txt)
    txt_submissions = [s for s in txt_subreddit.get_top_from_month(limit=n_imgs*5)]
    random.shuffle(txt_submissions)
    img_subreddit = r.get_subreddit(source_img)
    img_submissions = [s for s in img_subreddit.get_top_from_month(limit=n_imgs*5)]
    random.shuffle(img_submissions)

    # NSFW filter:
    if not nsfw_ok:
        txt_submissions = [s for s in txt_submissions if not s.over_18]
        img_submissions = [s for s in img_submissions if not s.over_18]

    # Output folder handling
    if clear_before_output and out_path != '':
        shutil.rmtree(out_path)
    os.makedirs(out_path, exist_ok=True)

    # Image generation loop
    files_written = 0
    for s in np.arange(min([len(txt_submissions), len(img_submissions)])):
        if files_written >= n_imgs:
            continue

        # Load the image
        img_url = img_submissions[s].preview['images'][0]['source']['url']
        img = imageio.imread(img_url)

        if no_portraits and (img.shape[0] > img.shape[1]):
            continue
        if no_landscapes and (img.shape[0] < img.shape[1]):
            continue

        img_pil = Image.fromarray(img).convert('RGBA')
        quote = txt_submissions[s].title
        quote_rows = '\n'.join(textwrap.wrap(quote, width=line_length))
        try:
            img_attrib = 'Image by /u/{} from {}'.format(
                img_submissions[s].author.name, img_submissions[s].short_link)
        except AttributeError:
            img_attrib = 'Image from {}'.format(
                img_submissions[s].short_link)
        try:
            txt_attrib = 'Quote by /u/{} from {}'.format(
                txt_submissions[s].author.name, txt_submissions[s].short_link)
        except:
            txt_attrib = 'Quote from {}'.format(
                txt_submissions[s].short_link)

        # Need blank image template
        txt_img = Image.new('RGBA', img_pil.size, (255,255,255,0))

        # Generate fonts
        big_size = round(img.shape[1]*0.90/(line_length/2))
        small_size = round(big_size/4.0)
        big_font = ImageFont.truetype(font_file.name, size=big_size)
        small_font = ImageFont.truetype(font_file.name, size=small_size)

        # Generate a drawing context
        d = ImageDraw.Draw(txt_img)

        # Draw quote
        quote_size = d.multiline_textsize(quote_rows, font=big_font)
        quote_xloc = round(img.shape[1]/2-quote_size[0]/2)
        if quote_location == 'bottom':
            quote_yloc = round(img.shape[0]-(quote_size[1]+big_size*1.0))
        elif quote_location == 'middle':
            quote_yloc = round(img.shape[0]/2-(quote_size[1]+big_size*1.0)/2)
        elif quote_location == 'top':0round(0)
        d.multiline_text((quote_xloc+big_size*0.05, quote_yloc+big_size*0.05),
                         quote_rows, font=big_font, align='center', fill=(0, 0, 0, 192))
        d.multiline_text((quote_xloc, quote_yloc),
                         quote_rows, font=big_font, align='center', fill=(255, 255, 255, 255))

        # Draw attributions
        img_attrib_size = d.textsize(img_attrib, font=small_font)
        img_attrib_xloc = round(small_size/2.0)
        img_attrib_yloc = round(img.shape[0]-(img_attrib_size[1]+small_size/2.0))
        d.text((img_attrib_xloc, img_attrib_yloc),
               img_attrib, font=small_font, fill=(255, 255, 255, 128))
        txt_attrib_size = d.textsize(txt_attrib, font=small_font)
        txt_attrib_xloc = round(img.shape[1]-(txt_attrib_size[0]+small_size/2.0))
        txt_attrib_yloc = round(img.shape[0]-(txt_attrib_size[1]+small_size/2.0))
        d.text((txt_attrib_xloc, txt_attrib_yloc),
               txt_attrib, font=small_font, fill=(255, 255, 255, 128))
        out = Image.alpha_composite(img_pil, txt_img)
        out = np.asarray(out)

        # Done, write to output file
        imageio.imwrite(os.path.join(out_path, 'output_{}.jpg'.format(files_written)), out[...,0:3])
        files_written = files_written + 1

if __name__ == "__main__":
    _click_main()