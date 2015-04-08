#include <Python.h>
#include <structmember.h>

#include "regex2dfa.h"

typedef struct {
    PyObject_HEAD
} Regex2dfaObject;

static PyObject * Regex2dfa__regex2dfa(PyObject *self, PyObject *args) {
    char* word;
    uint32_t len;

    if (!PyArg_ParseTuple(args, "s#", &word, &len))
        return NULL;

    const std::string input_regex = std::string(word, len);

    std::string minimized_dfa;
    try {
        regex2dfa::Regex2Dfa(input_regex, &minimized_dfa);
    } catch (std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return 0;
    }

    PyObject *retval = PyString_FromString((char*)(minimized_dfa.c_str()));

    return retval;
}

static PyObject *
Regex2dfa_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Regex2dfaObject *self;
    self = (Regex2dfaObject *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
Regex2dfa_init(Regex2dfaObject *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static void
Regex2dfa_dealloc(PyObject* self)
{
    if (self != NULL)
        PyObject_Del(self);
}

static PyMethodDef Regex2dfa_methods[] = {
    {NULL, NULL, 0, NULL}
};


static PyTypeObject Regex2dfaType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "Regex2dfa",
    sizeof(Regex2dfaObject),
    0,
    Regex2dfa_dealloc,             /*tp_dealloc*/
    0,                       /*tp_print*/
    0,                       /*tp_getattr*/
    0,                       /*tp_setattr*/
    0,                       /*tp_compare*/
    0,                       /*tp_repr*/
    0,                       /*tp_as_number*/
    0,                       /*tp_as_sequence*/
    0,                       /*tp_as_mapping*/
    0,                       /*tp_hash */
    0,			     /* tp_call */
    0,			     /* tp_str */
    0,  		     /* tp_getattro */
    0,		   	     /* tp_setattro */
    0,			     /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE,     /*tp_flags*/
    0,			     /* tp_doc */
    0,			     /* tp_traverse */
    0,			     /* tp_clear */
    0,			     /* tp_richcompare */
    0,			     /* tp_weaklistoffset */
    0,			     /* tp_iter */
    0,			     /* tp_iternext */
    Regex2dfa_methods,	     /* tp_methods */
    0,			     /* tp_members */
    0,		   	     /* tp_getset */
    0,			     /* tp_base */
    0,			     /* tp_dict */
    0,			     /* tp_descr_get */
    0,			     /* tp_descr_set */
    0,		   	     /* tp_dictoffset */
    (initproc)Regex2dfa_init,	     /* tp_init */
    0,			     /* tp_alloc */
    Regex2dfa_new,		     /* tp_new */
    0,			     /* tp_free */
};


static PyMethodDef ftecRegex2dfaMethods[] = {
    {"regex2dfa",  Regex2dfa__regex2dfa, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};


#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initcRegex2dfa(void)
{
    if (PyType_Ready(&Regex2dfaType) < 0)
        return;

    PyObject *m;
    m = Py_InitModule("cRegex2dfa", ftecRegex2dfaMethods);
    if (m == NULL)
        return;

    Py_INCREF(&Regex2dfaType);
    PyModule_AddObject(m, "Regex2dfa", (PyObject *)&Regex2dfaType);
}
