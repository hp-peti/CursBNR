using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Drawing.Drawing2D;
using System.Globalization;
using System.Xml;
using System.IO;

namespace CursBNR
{
    using ValueDictionary = SortedDictionary<DateTime, double>;

    public partial class TrendForm : Form
	{
		public class GraphPoint
		{
			public DateTime Date { get; set; }
			public double Value { get; set; }
		};

		private class DrawString
		{
			public float X { get; set; }
			public float Y { get; set; }
			public string Text { get; set; }
		}

		private class DrawLine
		{
			public float X1 { get; set; }
			public float Y1 { get; set; }
			public float X2 { get; set; }
			public float Y2 { get; set; }
		}

		public TrendForm()
		{
			InitializeComponent();
			Font = SystemFonts.MessageBoxFont;
			MinimumSize = new Size(Width, 2 * Height / 3);
		}

		public TrendForm(DateTime begin, DateTime end, string currency, DateTime maxDate)
			: this()
		{
			dateBegin.Value = begin;
			dateBegin.MaxDate = maxDate;
			dateEnd.Value = end;
			dateEnd.MaxDate = maxDate;
			lblCurrency.Text = currency;
			if (!staticValues.TryGetValue(currency, out values))
			{
				values = new ValueDictionary();
				staticValues.Add(currency, values);
			}
		}
		//static bool asyncBusy = false;
		static IDictionary<string, ValueDictionary> staticValues = new SortedDictionary<string, ValueDictionary>();
		ValueDictionary values;

		List<GraphPoint> graph = null;

		public static readonly string FMT_NUMBER = "0.00######";

		public static double Round(double value, int digits)
		{
			var pow = Math.Pow(10, -digits);
			return Math.Round(value / pow) * pow;
		}

		private void GenerateGraph()
		{
			if (graph.Count < 2)
			{
				boxGraph.Image = null;
				return;
			}
			if (boxGraph.Width < 10 || boxGraph.Height < 10)
			{
				return;
			}

			var size = boxGraph.ClientSize;

			Bitmap bmp = new Bitmap(size.Width, size.Height);
			var font = SystemFonts.MessageBoxFont;

			using (var g = Graphics.FromImage(bmp))
			{
				Color backColor = SystemColors.Window;
				Color frontColor = SystemColors.WindowText;
				Color grayColor = SystemColors.GrayText;
				Color lineColor = frontColor;

				Brush backBrush = new SolidBrush(backColor);
				Brush textBrush = new SolidBrush(frontColor);
				Pen linePen = new Pen(lineColor, 2.5f);
				linePen.EndCap = LineCap.Round;
				linePen.StartCap = LineCap.Round;
				Brush pointBrush = new SolidBrush(lineColor);
				Pen gridPen = new Pen(grayColor, 1);
				gridPen.DashStyle = DashStyle.Solid;
				var half = MixColors(grayColor, .25f, backColor, .75f);
				Pen gridLightPen = new Pen(half, 1);
				gridLightPen.DashStyle = DashStyle.Solid;

				var dateText = new List<DrawString>();
				var valueText = new List<DrawString>();
				var drawLines = new List<DrawLine>();

				g.SmoothingMode = SmoothingMode.AntiAlias;
				g.FillRectangle(backBrush, 0, 0, size.Width, size.Height);

				double minValue = graph[0].Value;
				double maxValue = graph[0].Value;
				for (int i = 1; i < graph.Count; ++i)
				{
					if (graph[i].Value < minValue)
						minValue = graph[i].Value;
					if (graph[i].Value > maxValue)
						maxValue = graph[i].Value;
				}

				const double resolution = 0.0001;


				if (Math.Abs(minValue - maxValue) < resolution)
				{
					var extra = Math.Min(minValue / 2, resolution);
					minValue -= extra;
					maxValue += extra;
				}

				var minDate = graph[0].Date;
				var maxDate = graph[graph.Count - 1].Date;

				var numberSize = g.MeasureString("0.0000", font);
				float fontHeight = numberSize.Height * .8f;

				int extraTop = (int)numberSize.Height;
				int extraLeft = (int)numberSize.Width + 10;
				int extraRight = (int)numberSize.Height;
				int extraBottom = (int)numberSize.Width;

				double scaleX = (double)(size.Width - (extraLeft + extraRight)) / (maxDate - minDate).TotalDays;
				double offsetX = 0 * scaleX + extraLeft;
				double scaleY = -(size.Height - extraTop - extraBottom) / (maxValue - minValue);
				double offsetY = size.Height - extraBottom + -minValue * scaleY;

				var dayWidth = scaleX;

				var sameYear = minDate.Year == maxDate.Year;
				var sameMonth = sameYear && minDate.Month == maxDate.Month;

				var daily = dayWidth >= fontHeight;

				var fitWeekly = !daily && dayWidth * 7 >= fontHeight;
				var monthly = !daily && dayWidth * 30 >= fontHeight;
				var yearly = !daily && !monthly;

				for (int i = 0; i < graph.Count; ++i)
				{
					var date = graph[i].Date;
					var month = date.Month;
					var day = date.Day;
					var dayOfWeek = date.DayOfWeek;
					var draw = false;
					string format = null;
					if (yearly)
					{
						if (day == 1)
						{
							draw = true;
							if (month == 1)
							{
								format = "yyyy";
							}
						}
					}
					else if (monthly)
					{
						if (day == 1)
						{
							draw = true;
							if (month == 1)
							{
								if (fitWeekly)
								{
									format = "dd MMM yyyy";
								}
								else
								{
									format = "MMM yyyy";
								}
							}
							else
							{
								if (fitWeekly)
								{
									format = "dd MMM";
								}
								else
								{
									format = "MMM";
								}
							}
						}
						else
						{
							draw = fitWeekly;
							if (fitWeekly)
							{
								draw = true;
								if (dayOfWeek == DayOfWeek.Monday)
								{
									if (day * scaleX > fontHeight)
									{
										format = string.Empty;
										int rday = DateTime.DaysInMonth(date.Year, month) - day + 1;
										if (rday * scaleX > fontHeight)
										{
											format = "dd";
										}
									}
								}
							}
						}
					}
					else
					{
						draw = true;
						if (month == 1 && day == 1)
						{
							format = "dd MMM yyyy";
						}
						else if (day == 1)
						{
							format = "dd MMM";
						}
						else
						{
							format = "dd";
						}
					}

					if (draw)
					{
						var x = (float)((graph[i].Date - minDate).TotalDays * scaleX + offsetX);
						if (format != null)
						{
							if (format.Length > 0)
							{
								dateText.Add(new DrawString
								{
									X = x - fontHeight * .2f,
									Y = size.Height,
									Text = date.ToString(format)
								});
							}
							drawLines.Add(new DrawLine { X1 = x, Y1 = 0, X2 = x, Y2 = size.Height });
						}
						else
						{
							g.DrawLine(gridLightPen, x, 0, x, size.Height);
						}
					}
				}


				var precY = (int)Math.Floor(Math.Log10(Math.Abs(scaleY) / fontHeight));

				var dotSize = Math.Min((float)scaleX / 2, 10);
				if (Math.Abs(dotSize) < 1)
				{
					dotSize = 0;
				}

				var startY = Round(minValue, precY);
				var endY = Round(maxValue, precY);
				var stepY = Math.Pow(10, -precY);

				int div = 1;
				int mod = 0;

				while (Math.Abs(scaleY) * (stepY / 2) > fontHeight)
				{
					stepY = stepY / 2;
					startY -= stepY;
					endY += stepY;

					div *= 2;
					mod = (mod * 2 + div - 1) % div;
				}
				for (var valueY = startY; valueY < endY; valueY += stepY)
				{
					var y = (float)(valueY * scaleY + offsetY);
					if (mod == 0)
					{
						drawLines.Add(new DrawLine
						{
							X1 = 0,
							Y1 = y,
							X2 = size.Width,
							Y2 = y
						});
					}
					else
					{
						g.DrawLine(gridLightPen, 0, y, size.Width, y);
					}
					valueText.Add(new DrawString
					{
						X = 0,
						Y = y - fontHeight,
						Text = valueY.ToString(FMT_NUMBER, CultureInfo.InvariantCulture)
					});

					mod = (mod + 1) % div;
				}

				foreach (var dl in drawLines)
				{
					g.DrawLine(gridPen, dl.X1, dl.Y1, dl.X2, dl.Y2);
				}
				var matrix = g.Transform;
				try
				{
					foreach (var dt in dateText)
					{
						g.Transform = matrix;
						g.TranslateTransform(dt.X, dt.Y);
						g.RotateTransform(-90);
						g.DrawString(dt.Text, font, textBrush, 0, 0);
					}
				}
				finally
				{
					g.Transform = matrix;
				}
				foreach (var dt in valueText)
				{
					g.DrawString(dt.Text, font, textBrush, dt.X, dt.Y);
				}


				PointF last = new PointF(
					(float)((graph[0].Date - minDate).TotalDays * scaleX + offsetX),
					(float)(graph[0].Value * scaleY + offsetY)
				);
				DrawDot(g, pointBrush, last, dotSize);

				for (int i = 0; i < graph.Count; ++i)
				{
					PointF curr = new PointF(
						(float)((graph[i].Date - minDate).TotalDays * scaleX + offsetX),
						(float)(graph[i].Value * scaleY + offsetY)
					);
					g.DrawLine(linePen, last, curr);
					last = curr;
					DrawDot(g, pointBrush, last, dotSize);
				}
			}
			boxGraph.Image = bmp;
		}

		static void DrawDot(Graphics g, Brush brush, PointF point, float diameter)
		{
			const double epsilon = 1e-8;
			if (Math.Abs(diameter) < epsilon)
				return;
			float radius = diameter / 2;
			g.FillEllipse(brush, point.X - radius, point.Y - radius,
				diameter + .5f, diameter + .5f);
		}

		#region Persistence

		const string NODE_VALUES = "values";
		const string NODE_CURRENCY = "currency";
		const string ATTR_NAME = "name";
		const string ATTR_DATE = "date";
		const string ATTR_VALUE = "value";
		const string NODE_RATE = "rate";
		const string FMT_DATE = "yyyy-MM-dd";

		public static void LoadValues(string fileName)
		{
			using (var fileStream =
				new FileStream(fileName, FileMode.Open, FileAccess.Read))
			{
                var settings = new XmlReaderSettings();
                settings.IgnoreWhitespace = true;
                settings.IgnoreProcessingInstructions = true;
                settings.IgnoreComments = true;
				using (var reader = XmlReader.Create(fileStream, settings))
				{
                    if (reader.ReadToDescendant(NODE_VALUES))
                    {
                        do
                        {
                            ReadValues(reader.ReadSubtree());
                        }
                        while (reader.ReadToNextSibling(NODE_VALUES));
                    }
				}
			}
		}

		private static void ReadValues(XmlReader reader)
		{
            if (reader.ReadToDescendant(NODE_CURRENCY))
            {
                do
                {
                    string name = null;
                    if (reader.MoveToFirstAttribute())
                    {
                        do
                        {
                            switch (reader.Name)
                            {
                                case ATTR_NAME:
                                    name = reader.Value;
                                    break;
                            }
                        }
                        while (name == null &&
                            reader.MoveToNextAttribute());

                        reader.MoveToElement();
                    }
                    if (name != null)
                    {
                        ReadCurrency(name, reader.ReadSubtree());
                    }
                }
                while (reader.ReadToNextSibling(NODE_CURRENCY));
            }
        }

		private static void ReadCurrency(string name, System.Xml.XmlReader reader)
		{
			var values = new ValueDictionary();
			if (reader.ReadToDescendant(NODE_RATE))
            {
                do
                {
                    DateTime? date = null;
                    double? rate = null;
                    if (reader.MoveToFirstAttribute())
                    {
                        do
                        {
                            switch (reader.Name)
                            {
                                case ATTR_DATE:
                                    date = DateTime.ParseExact(reader.Value, FMT_DATE, CultureInfo.InvariantCulture);
                                    break;
                                case ATTR_VALUE:
                                    rate = double.Parse(reader.Value, CultureInfo.InvariantCulture);
                                    break;
                            }
                        }
                        while (reader.MoveToNextAttribute());
                    }
                    if (date.HasValue && rate.HasValue && rate.Value > 0)
                    {
                        values[date.Value] = rate.Value;
                    }
                } while (reader.ReadToNextSibling(NODE_RATE));
            }
            staticValues[name] = values;
		}

		public static void SaveValues(string fileName)
		{
			using (var fileStream = new FileStream(fileName, FileMode.Create, FileAccess.Write))
			{
				using (var writer = new XmlTextWriter(fileStream, Encoding.UTF8))
				{
					writer.Formatting = Formatting.Indented;
					writer.Indentation = 1;
					writer.IndentChar = '\t';
					writer.QuoteChar = '\'';
					writer.WriteStartDocument();
					{
						writer.WriteStartElement(NODE_VALUES);
						{
							foreach (var curr in staticValues)
							{
								writer.WriteStartElement(NODE_CURRENCY);
								{
									writer.WriteStartAttribute(ATTR_NAME);
									{
										writer.WriteValue(curr.Key);
									}
									writer.WriteEndAttribute();

									foreach (var rate in curr.Value)
									{
										if (rate.Value > 0)
										{
											writer.WriteStartElement(NODE_RATE);
											{
												writer.WriteStartAttribute(ATTR_DATE);
												{
													writer.WriteValue(rate.Key.ToString(FMT_DATE, CultureInfo.InvariantCulture));
												}
												writer.WriteEndAttribute();
												writer.WriteStartAttribute(ATTR_VALUE);
												{
													writer.WriteValue(rate.Value.ToString(CultureInfo.InvariantCulture));
												}
												writer.WriteEndAttribute();
											}
											writer.WriteEndElement();
										}
									}
								}
								writer.WriteEndElement();
							}
						}
						writer.WriteFullEndElement();
					}
					writer.WriteEndDocument();
				}
			}
		}

		#endregion

		private void btnGet_Click(object sender, EventArgs e)
		{
			Get(dateBegin.Value, dateEnd.Value);
		}

		private void Get(DateTime begin, DateTime end)
		{
			var curs = CursForm.GetCurs();
			btnGet.Enabled = false;
			try
			{
				graph = new List<GraphPoint>();
				var date = begin.Date;
				end = end.Date;
				string currency = lblCurrency.Text;
				progress.Minimum = 0;
				progress.Maximum = Math.Max((end - begin).Days, 0);
				progress.Value = 0;
				progress.Step = 1;
				while (date <= end)
				{
					double value;

					if (!values.TryGetValue(date, out value))
					{
						value = Double.NaN;
						bool wait = true;
						GetValueCompletedEventHandler getValueCompleted = null;
						getValueCompleted = delegate(object sender, GetValueCompletedEventArgs args)
						{
							if (args.UserState == this)
							{
								wait = false;
								curs.GetValueCompleted -= getValueCompleted;
								if (args.Error == null && !args.Cancelled)
								{
									value = args.Result;
								}
							}
						};
						curs.GetValueCompleted += getValueCompleted;
						curs.GetValueAsync(date, currency, this);

						while (wait && Application.OpenForms.Count > 0)
						{
							Application.DoEvents();
							System.Threading.Thread.Sleep(1);
						}
						if (!Double.IsNaN(value))
						{
							values.Add(date, value);
						}
						else
						{
							return;
						}
					}
					if (!Double.IsNaN(value) && value > 0)
					{
						graph.Add(new GraphPoint { Date = date, Value = value });
						timerGraph.Start();
					}
					date = date.AddDays(1);
					progress.Increment(1);
				}
			}
			finally
			{
				btnGet.Enabled = true;
			}
		}

		private void boxGraph_Resize(object sender, EventArgs e)
		{
			timerGraph.Start();
		}

		private void timer1_Tick(object sender, EventArgs e)
		{
			timerGraph.Stop();
			if (FormWindowState.Minimized != WindowState)
			{
				if (graph == null)
				{
					Get(dateBegin.Value, dateEnd.Value);
				}
				GenerateGraph();
			}
		}

		private void TrendForm_Shown(object sender, EventArgs e)
		{
			timerGraph.Start();
		}

		private Color MixColors(Color colorA, float alphaA, Color colorB, float alphaB)
		{
			return Color.FromArgb(
				(int)(colorA.A * alphaA + colorB.A * alphaB),
				(int)(colorA.R * alphaA + colorB.R * alphaB),
				(int)(colorA.G * alphaA + colorB.G * alphaB),
				(int)(colorA.B * alphaA + colorB.B * alphaB)
				);
		}

		private void TrendForm_FormClosing(object sender, FormClosingEventArgs e)
		{
			if (btnGet.Enabled == false)
			{
				e.Cancel = true;
			}
		}


	}


}
