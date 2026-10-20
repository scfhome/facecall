"""CLI 主入口模块"""

import sys
from getpass import getpass

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .client import CUCNClient, LoginCredentials

console = Console()


def main():
    """CLI 主函数"""
    console.print(
        Panel.fit(
            "[bold cyan]中国传媒大学南广学院教务系统登录工具[/bold cyan]",
            border_style="cyan",
        )
    )

    # 获取登录凭据
    username = input("请输入用户名: ").strip()
    if not username:
        console.print("[red]错误：用户名不能为空[/red]")
        sys.exit(1)

    password = getpass("请输入密码: ")
    if not password:
        console.print("[red]错误：密码不能为空[/red]")
        sys.exit(1)

    credentials = LoginCredentials(username=username, password=password)
    client = CUCNClient()

    # 执行登录
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在登录...", total=None)

        result = client.login(credentials)

        progress.update(task, completed=True)

    # 显示结果
    if result.success:
        console.print(
            Panel(
                f"[bold green]✓ {result.message}[/bold green]\n\n"
                f"[dim]Session ID:[/dim] {result.session_id}",
                title="登录成功",
                border_style="green",
            )
        )

        # 尝试激活点名模块
        console.print("\n[dim]正在激活教师点名模块...[/dim]")
        success, message = client.activate_module()

        if success:
            console.print(f"[green]✓ 模块激活成功: {message}[/green]")
        else:
            console.print(f"[yellow]! 模块激活失败: {message}[/yellow]")

        # 获取用户信息
        console.print("\n[dim]获取用户信息...[/dim]")
        user_info = client.get_user_info()
        console.print(f"[cyan]状态: {user_info.get('status')}[/cyan]")

        sys.exit(0)

    else:
        console.print(
            Panel(
                f"[bold red]✗ {result.message}[/bold red]\n\n"
                f"[dim]错误详情:[/dim]\n{result.error or '无详情'}",
                title="登录失败",
                border_style="red",
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
