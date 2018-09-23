## 分析计算脚本

1. 运行并分析单个脚本

```sh
python -m cProfile simple_kmean.py
```

2. 分析脚本中的部分语句和过程

```sh
python simple_kmean_add_profiling.py
```

注意脚本中`test_kmean`函数内新增的profiler调用。

脚本还生成了profile结果文件。可以用pstats库打开进行后续分析：

```sh
python -m pstats simple_kmean_add_profiling.pstats
```


3. 绘图分析

下载并安装[graphviz](https://www.graphviz.org/download/)。默认安装路径为`C:\Program Files (x86)\Graphviz2.38\bin\dot.exe`

执行

```sh
# windows
python -m gprof2dot -f pstats simple_kmean_add_profiling.pstats | "C:\Program Files (x86)\Graphviz2.38\bin\dot.exe" -Tpng -o output.png

# Linux/OSX
python -m gprof2dot -f pstats simple_kmean_add_profiling.pstats | dot -Tpng -o output.png
```

其中`simple_kmean_add_profiling.pstats`文件来自第2步脚本的输出。

4. 逐行分析

安装[line_profiler](https://github.com/rkern/line_profiler)，Windows安装比较麻烦，推荐Linux下使用。

执行

```sh
kernprof -l simple_kmean_line_profiler.py
```

注意`test_kmean`函数定义前增加了一个`@profile`装饰器，但装饰器没有导入。这个装饰器在运行时会被kernprof注入。

执行结束后，可以查看结果

```sh
python -m line_profiler simple_kmean_line_profiler.py.lprof
```

## 分析WEB应用（以Flask为例）

一般执行Flask应用，使用的命令是：

```sh
# Windows
set FLASK_APP=flask_app.py
flask run

# Linux/OSX
export FLASK_APP=flask_app.py
flask run
```

为了注入profiler，需要从WSGI APP启动：

```sh
python flask_wsgi.py
```

WSGI中增加了profile中间件，如果不指定`profile_dir`参数，结果会被输出到stderr；否则结果会存为prof文件，可以用前述方法分析。
