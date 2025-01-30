Dataset **PubTables-1M: Detection** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/remote/eyJsaW5rIjogImZzOi8vYXNzZXRzLzMxNzJfUHViVGFibGVzLTFNOiBEZXRlY3Rpb24vcHVidGFibGVzMW0tZGV0ZWN0aW9uLURhdGFzZXROaW5qYS50YXIiLCAic2lnIjogInpRWUFDMzRtSjU5Z2F2VDBNdEhIV0YxeS96TTdSdmJkM2V0QlNnMGV4Wms9In0=)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='PubTables-1M: Detection', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be downloaded here:

- [PubTables-1M-Detection_Annotations_Test.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Annotations_Test.tar.gz?download=true)
- [PubTables-1M-Detection_Annotations_Train.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Annotations_Train.tar.gz?download=true)
- [PubTables-1M-Detection_Annotations_Val.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Annotations_Val.tar.gz?download=true)
- [PubTables-1M-Detection_Filelists.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Filelists.tar.gz?download=true)
- [PubTables-1M-Detection_Images_Test.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Images_Test.tar.gz?download=true)
- [PubTables-1M-Detection_Images_Train_Part1.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Images_Train_Part1.tar.gz?download=true)
- [PubTables-1M-Detection_Images_Train_Part2.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Images_Train_Part2.tar.gz?download=true)
- [PubTables-1M-Detection_Images_Val.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Images_Val.tar.gz?download=true)
- [PubTables-1M-Detection_Page_Words.tar.gz](https://huggingface.co/datasets/bsmock/pubtables-1m/resolve/main/PubTables-1M-Detection_Page_Words.tar.gz?download=true)
