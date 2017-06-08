图灵社区样书爬虫
================

图灵社区改了新版后，样书兑换列表不见了，于是自己动手丰衣足食。

安装依赖
--------


.. code-block:: bash

   $ sudo pip install django
   $ sudo pip install beautifulsoup4
   $ sudo pip install redis
   $ sudo pip install jieba


爬虫抓取的数据存在 redis 上（偷懒），所以要先安装 redis。程序在 Python2.7 和 3.5+ 上测试通过。

运行
----

.. code-block:: python

   python app.py runserver

然后访问 http://localhost:8000/books 即可，这里假设你使用默认端口。

turing.py 是实际上的爬虫，你需要使用 Crontab 定时执行它，请不要过于频繁以免对图灵服务器造成压力。

以下是我的 Crontab 设置：

::

   0 9-21/3 * * * python3 /home/ubuntu/code/ituring/turing.py new
   0 5 * * * python3 /home/ubuntu/code/ituring/turing.py all

即早上 9 点至晚上 9 天每 3 小时更新一次最新的100本书的可兑换情况，每天早上 5 点更新全部图书的可兑换情况。

杂项
----

如果你使用 Windows，没有 Crontab，你可以试试 `uCron <https://github.com/akgnah/ucron/>`_ 并修改 app.py 创建一个 URL 以便访问 turing.py。

因为爬虫比较简单，所以没有注释，如果你有任何疑问欢迎 Email 联系我。在我的 Github 主页能找到我的邮箱地址。

谢谢。
