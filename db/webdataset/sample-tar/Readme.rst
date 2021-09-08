Contents
========

+--------------------+-------------------------------+
| File               | Description                   |
+====================+===============================+
| empty.tar          | a tar file with no entries    |
+--------------------+-------------------------------+
| gnu.tar            | a tar file with over 120      |
|                    | characters long names         |
+--------------------+-------------------------------+
| oldgnu.tar         | a tar file in an oldgnu       |
|                    | tar format                    |
+--------------------+-------------------------------+
| v7.tar             | a tar file in the pre-ansi    |
|                    | tar format                    |
+--------------------+-------------------------------+
| types.tar          | a tar file with entries       |
|                    | of all possible types         |
+--------------------+-------------------------------+
| cross.tar          | a webdataset archive for      |
|                    | the cross-check test          |
|                    | containing files that         |
|                    | with a dot, non-file entries, |
|                    | and missing extensions        |
+--------------------+-------------------------------+
| dtypes.tar         | a webdataset archive with     |
|                    | files filled in with a        |
|                    | byte representation of the    |
|                    | index of the sample in        |
|                    | float16, int32 and float64,   |
|                    | repeated 10 times             |
+--------------------+-------------------------------+
| hidden.tar         | a webdataset archive with     |
|                    | all samples starting with     |
|                    | a dot                         |
+--------------------+-------------------------------+
| single.tar         | a webdataset archive with     |
|                    | a single sample with a        |
|                    | single component              |
+--------------------+-------------------------------+
| single_junk.tar    | a webdataset archive with     |
|                    | a single sample with a        |
|                    | single component, and some    |
|                    | non-file entries next to it   |
|                    | (that have the same name      |
|                    | as the sample but different   |
|                    | extensions)                   |
+--------------------+-------------------------------+
| types_contents.tar | a webdataset archive with     |
|                    | entries of all possible types |
|                    | and file entries having 16    |
|                    | bytes of zeros                |
+--------------------+-------------------------------+
| wide.tar           | a webdataset archive with     |
|                    | a single sample with a 1000   |
|                    | components                    |
+--------------------+-------------------------------+
