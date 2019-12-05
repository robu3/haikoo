# haikoo 🖋

[日本語はこちら](#日本語版)

Haikoo is a fun little haiku generator. It uses [Azure Congnitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/), Markov chains (leveraging [Markovify](https://github.com/jsvine/markovify)), and word syllable counts to create haiku from an image. The text is then overlaid on a cropped version of the original picture to create a consolidated image ready for social media.

Given an image like this:

![Input](/sample_input.jpeg?raw=true)

It produces something like this:

![Output](/sample_output.png?raw=true)

## Basic Usage

Haikoo can be used as module or as a command line utility.

As a module:

```python
from haikoo.haikoo import Haikoo, ImageDescriber

# instantiate image describer and haikoo
# the markov model can be: fusion (recommended), shakespeare, frost, or classic
describer = ImageDescriber("azure_cv_key", "azure_cv_region")
haikoo = Haikoo(describer, "fusion")

# then create your haiku!
haiku = haikoo.create_image(file_path=args.image, out_file_path=args.out, text=args.text)
```

From the terminal:

```
python app.py /path/to/image.png
```

When using the terminal application, you will need to copy config.json.default to config.json and update the file with your Azure CV key and region before beginning.
Let the programmatically generated poetry begin!

## Technical Details

Haikoo extends/subclasses a couple of Markovify's classes in order to create Markov chain models that also take syllable count into consideration when selecting words, i.e., `HaikuChain` and `HaikuText`. `HaikuChain` counts the number of syllables in a word when tokenizing text; the result can be serialized for reuse later, negating the need to count syllables at runtime (a performance win).

## Advanced Usage

The Azure Computer Vision-based `ImageDescriber` can swapped out with another implementation by passing it into the constructor; see the `MockImageDescriber` for an example.

```python
from haikoo.haikoo import Haikoo, MyCustomImageDescriber

describer = MyCustomImageDescriber()
haikoo = Haikoo(describer, "fusion")
```

# 日本語版
# haikoo 🖋

「Haikoo」というのは楽しい俳句ジェネレータです。[Azure Congnitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/)、 マルコフ連鎖 ([Markovify](https://github.com/jsvine/markovify)を生かして)、 と言葉の音節数を使って絵から俳句を作ります。その俳句は元の絵の上に重なって出来上がり、ソーシャルメディアにもピッタリ！

こういう絵にすれば：

![Input](/sample_input.jpeg?raw=true)

こんなんが出て来る：

![Output](/sample_output.png?raw=true)

## 基本の使い方

「Haikoo」はモジュールかコマンドライン・インタフェースとして使えます。

モジュールとして：

```python
from haikoo.haikoo import Haikoo, ImageDescriber

# instantiate image describer and haikoo
# the markov model can be: fusion (recommended), shakespeare, frost, or classic
describer = ImageDescriber("azure_cv_key", "azure_cv_region")
haikoo = Haikoo(describer, "fusion")

# then create your haiku!
haiku = haikoo.create_image(file_path=args.image, out_file_path=args.out, text=args.text)
```

CLIとして:

```
python app.py /path/to/image.png
```

コマンドライン・インタフェースを使う時は始める前に`config.json.default`を`config.json`にコピーして、Azureのキーと地域を更新しなければなりません。

さぁ、俳句ジェネレータ開始！

## 技術詳細 

「Haikoo」は言葉の選ばれる時に音節数を考えるマルコフ連鎖を作るため、Markovifyのクラスを建て増します。例えば、`HaikuChain`と`HaikuText`。 `HaikuChain`はトークン化しながら音節数を数え、その結果はシリアライズする事も可能。ランタイムにしなくてもいいので性能アップ！

## 高度な使い方

「Azure Computer Vision」に基づいている`Image Describer`は他のインプリメンテーションをコンストラクタに入れて変えられます。例については`MockImageDescriber`を参照してください。

```python
from haikoo.haikoo import Haikoo, MyCustomImageDescriber

describer = MyCustomImageDescriber()
haikoo = Haikoo(describer, "fusion")
```