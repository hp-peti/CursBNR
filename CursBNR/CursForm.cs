using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Net;
using System.Globalization;

#pragma warning disable 0618

namespace CursBNR
{
	public partial class CursForm : Form
	{
		static Curs curs = GetCurs();
		decimal cursValue = 0;
		string curr = "EUR";


		public static Curs GetCurs()
		{
			if (curs == null)
			{
				curs = new Curs();
				var proxy = (WebProxy)WebProxy.GetDefaultProxy();
				if (proxy.Address != null)
				{
					proxy.Credentials = CredentialCache.DefaultNetworkCredentials;
					curs.Proxy = proxy;
				}
			}
			return curs;
		}

		public CursForm()
		{
			InitializeComponent();

			MinimumSize = Size;
			MaximumSize = new Size(2 * Width, Height);
			Font = SystemFonts.MessageBoxFont;
			dateCurs.MaxDate = curs.LastDateInserted();
		}

		private void btnGet_Click(object sender, EventArgs e)
		{
			Get();
		}

		private void Get()
		{
			var sel = cbCurr.Text;
			if (!string.IsNullOrEmpty(sel) && cbCurr.Items.Count > 0)
			{
				curr = sel;
			}
			DataTable table = curs.getall(dateCurs.Value.Date);
			table.PrimaryKey = new DataColumn[] { table.Columns[cbCurr.DisplayMember] };
			cbCurr.DataSource = table;
			cbCurr.SelectedIndex = table.Rows.IndexOf(table.Rows.Find(curr));
			Recalc();
		}
		private void cbIdMoneda_SelectionChangeCommitted(object sender, EventArgs e)
		{
			Recalc();
		}

		private void Recalc()
		{
			object value = cbCurr.SelectedValue;
			bool enable = value != null;
			if (enable)
			{
				cursValue = (decimal)Convert.ChangeType(value, typeof(decimal),CultureInfo.InvariantCulture);
				lblCurs.Text = cursValue.ToString(CultureInfo.InvariantCulture);
				var curr = cbCurr.Text;
				lblCurrValue.Text = curr;
				lblCurrResult.Text = curr;
				RecalcCurr();
				RecalcRON();
			}
			else
			{
				lblCurs.Text = string.Empty;
			}
			tableLayoutPanel2.Visible = enable;

		}

		public static readonly string FMT_NUMBER = "0.00##";

		private void RecalcCurr()
		{
			try
			{
				if (cursValue != 0)
				{
					var ron = decimal.Parse(tbRonValue.Text.Replace(',','.'), CultureInfo.InvariantCulture);
					var curr = ron / cursValue;
					tbCurrResult.Text = curr.ToString(FMT_NUMBER, CultureInfo.InvariantCulture);
				}
				btnTrend.Enabled = true;
			}
			catch (Exception)
			{
				tbCurrResult.Text = string.Empty;
				btnTrend.Enabled = false;
			}
			
		}

		private void RecalcRON()
		{
			try
			{
				if (cursValue != 0)
				{
					var curr = decimal.Parse(tbCurrValue.Text.Replace(',', '.'), CultureInfo.InvariantCulture);
					var ron = curr * cursValue;
					tbRonResult.Text = ron.ToString(FMT_NUMBER, CultureInfo.InvariantCulture);
				}
			}
			catch(Exception)
			{
				tbRonResult.Text = string.Empty;
			}
		}

		private void tbCurrValue_TextChanged(object sender, EventArgs e)
		{
			RecalcRON();
		}

		private void tbRonValue_TextChanged(object sender, EventArgs e)
		{
			RecalcCurr();
		}


		Dictionary<string, TrendForm> trends = new Dictionary<string, TrendForm>();

		private void btnTrend_Click(object sender, EventArgs e)
		{
			DateTime dateEnd = this.dateCurs.Value.Date;
			DateTime dateBegin = dateEnd.AddMonths(-1);
			DateTime maxDate = this.dateCurs.MaxDate;

			string curr = cbCurr.Text;
			TrendForm form;
			if (trends.TryGetValue(curr, out form))
			{
				form.WindowState = FormWindowState.Normal;
				form.BringToFront();
			}
			else
			{
				form = new TrendForm(dateBegin, dateEnd, curr, maxDate);
				form.FormClosed += delegate { trends.Remove(curr); };
				form.Show();
				trends.Add(curr,form);
			}


		}

		private void CursForm_Load(object sender, EventArgs e)
		{
			Get();
		}

	}
}
