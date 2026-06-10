# Using Python in R with `reticulate`

In this tutorial, we will demonstrate how to perform basic Python operations in R using the library `reticulate`. This includes converting between R and Python dataframe objects and running python functions. Since `scvi-tools` is written in Python, such an interface is necessary to take advantage of these models within the R environment.

### Import Libraries

```python
library(reticulate)
library(anndata)
library(sceasy)
library(Seurat)
library(SeuratData)
```

Before we use reticulate, we will need to point it to the correct conda env we use for the analysis

```python
use_condaenv("base", required = TRUE)
```

## Operating between Python and R

First, we will create a dummy list, and convert between R and Python. Note that R is 1-indexed while Python is 0-indexed, so when retrieiving elements the user should be conscious of what kind of object they are operating on.

```python
lst <- list(1, 2, 3)
print(lst)
print(typeof(lst))
```

We will convert this R list to a Python list via a function provided by the `reticulate` library called `r_to_py()`. This works for various fundamental R types like vectors, lists, arrays, data frames, functions, and primitives. Any python object will have `typeof(obj)` as `environment`. To see the Python type, we can call `class(obj)` instead.

```python
py_lst <- r_to_py(lst)
print(py_lst)
print(typeof(py_lst))
print(class(py_lst))
```

We can call instance functions of a Python object by replacing the usual dot notation with `$` instead. So something like `lst.append(5)` would become `lst$append(5)`.

```python
py_lst$append(5)
print(py_lst)
```

Note, arguments passed into these functions can either be Python or R objects. R objects passed in as arguments will automatically converted to the corresponding Python type via the `r_to_py()` function. However, this can sometimes result in unexpected results. For example, `0` in R will be automatically inferred as a float, which can result in an error when trying to pop an element below. We workaround this by explictly casting the R term to an integer with `as.integer(0)` or using the `0L` syntax, which results in the proper type conversion.

```python
# This will fail.
py_lst$pop(0)
```

```python
py_lst$pop(0L)
print(py_lst)
```

Finally, we will convert back into an R list with the function `py_to_r()` which executes the inverse of `r_to_py()`.

```python
lst <- py_to_r(py_lst)
print(lst)
```

## Import Python libraries

Now, we load the scanpy library via reticulate using the `import()` function. The `convert` boolean argument determines whether the output of Python functions is automatically converted to an R object equivalent via the `py_to_r()` function. Here, we set it to `FALSE` intentionally since often times we would like to retain the Python format for further manipulation in Python (e.g. with scanpy). Additionally, this keeps data type conversion more explicit, avoiding type confusion.

```python
py_config()
```

```python
sc <- import('scanpy', convert = FALSE)
```

## Load Dataset with SeuratData

```python
data("pbmc3k")
pbmc <- pbmc3k
```

```python
pbmc
```

In order to make use of `scvi-tools`, we use a third-party library called `sceasy` to convert the SeuratObject into an AnnData object, the primary format used by `scanpy` and `scvi-tools`.

```python
adata <- convertFormat(pbmc, from="seurat", to="anndata", main_layer="counts", drop_single_values=FALSE)
adata
```

We can access the AnnData fields in the same way we call instance functions, with the `$` syntax.

```python
adata$obs$head()
```

```python
class(adata$obs)
```

```python
head(py_to_r(adata$obs))
```

Above, we loaded the `anndata` R library. It is important to know when dealing with a Python AnnData object and an R AnnDataR6 Object. We can distinguish these by using the `class()` method, then using the `py_to_r(), r_to_py()` functions to interoperate between the two. Generally, it is recommended to use the R AnnDataR6 object to manipulate fields.

```python
class(adata)
```

```python
class(py_to_r(adata))
```

```python
# Convert adata object to R AnnDataR6 object.
adata <- py_to_r(adata)
```

We can set fields in the AnnData object using the `$` syntax. Here, we run CPM normalization using scanpy and save it to a new layer in the AnnData object. For the sake of demonstration, we do not use the inplace update option that scanpy provides. Note, this only works well if using the AnnDataR6 object.

```python
X_norm <- sc$pp$normalize_total(adata, target_sum = 1e+09, inplace = FALSE)["X"]
adata$layers["X_norm"] <- X_norm
```

```python
head(as.data.frame(adata$layers["X_norm"]))
```

Now you should be comfortable interoperating between R and Python. Once you configure your AnnData object to contain all the necessary fields for your model of choice, you can intialize and train with the AnnData object. Visit our tutorials page for examples of running `scvi-tools` in R.

## Session Info

```python
sI <- sessionInfo()
sI$loadedOnly <- NULL
print(sI, locale=FALSE)
```
