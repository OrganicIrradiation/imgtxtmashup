#imgtxtmashup
This is a simple script that creates desktop wallpapers mashing-up post titles and images from reddit.com. The [traditional usage](https://www.reddit.com/r/raspberry_pi/comments/46nb99/for_my_first_project_i_made_a_display_that_takes/) is to combine quotes from [/r/showerthoughts](https://reddit.com/r/showerthoughts) and [/r/earthporn](https://reddit.com/r/earthporn). I encourage you to try different combinations!

### Examples
Display information about the options and defaults:

```bash
$ python imgtxtmashup.py --help
```

Create a subfolder "output" with 10 images from [/r/earthporn](https://reddit.com/r/earthporn) and quotes from [/r/showerthoughts](https://reddit.com/r/showerthoughts):

```bash
$ python imgtxtmashup.py
```

Use an alternative set of source subreddits (images: [/r/spaceporn](https://reddit.com/r/spaceporn), text: [/r/shittyaskscience](https://reddit.com/r/shittyaskscience)) and create landscape images captions in the middle of the image:

```bash
$ python imgtxtmashup.py --source_txt shittyaskscience --source_img spaceporn --no_portraits --n_imgs 1 --quote_location middle
```

##Installation
Clone the package using git:

    git clone https://github.com/OrganicIrradiation/imgtxtmashup.git


##Requirements
Requires [click](https://pypi.python.org/pypi/click), [imageio](https://pypi.python.org/pypi/imageio), [numpy](https://pypi.python.org/pypi/numpy), [Pillow](https://pypi.python.org/pypi/Pillow), and [praw](https://pypi.python.org/pypi/praw).
