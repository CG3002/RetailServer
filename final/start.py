from retailserver import app, database, transactions, views
from retailserver.database import db, Product, TransactionTimestamp, TransactionDetails, PriceDisplayUnit
from retailserver.model_views import ProductAdmin, TransactionDescAdmin, TransactionStampAdmin, PriceDisplayUnitAdmin
from flask.ext.admin import Admin
from flask.ext.admin import BaseView, expose, AdminIndexView
from reportlab.pdfgen import canvas  
from reportlab.lib.units import cm 
import gevent
import serial, time
import gevent.monkey
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_all()
from flask import Flask, request, Response, render_template, redirect
import webbrowser, threading, requests, datetime, math, os, win32print, win32api
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import newreg

newreg.start()